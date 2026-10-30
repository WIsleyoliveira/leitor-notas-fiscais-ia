"""Leitor de Notas Fiscais com IA: foto ou PDF de nota/cupom -> planilha de lançamentos."""

import base64
import csv
import io
from typing import Literal

import streamlit as st
from pydantic import BaseModel, Field

from ia import ErroIA, extrair

Categoria = Literal[
    "alimentação", "combustível", "transporte", "hospedagem", "material de escritório",
    "tecnologia", "serviços", "saúde", "outros",
]


class Item(BaseModel):
    descricao: str
    quantidade: float
    valor_total: float


class Nota(BaseModel):
    emitente: str
    cnpj: str = Field(description="CNPJ do emitente no formato 00.000.000/0000-00, ou '' se ilegível")
    data_emissao: str = Field(description="AAAA-MM-DD, ou '' se ilegível")
    numero: str = Field(description="Número da nota ou cupom, ou ''")
    forma_pagamento: str = Field(description="Ex.: cartão de crédito, Pix, dinheiro; ou ''")
    itens: list[Item]
    valor_total: float
    categoria: Categoria
    confianca: Literal["alta", "média", "baixa"] = Field(
        description="Baixa se a imagem estiver borrada, cortada ou com campos ilegíveis"
    )


INSTRUCOES = """Você lê notas fiscais e cupons brasileiros (NF-e, NFC-e, cupom fiscal, recibo).
Extraia os campos pedidos exatamente como aparecem no documento. Valores em reais,
com ponto como separador decimal. Nunca invente um CNPJ, data ou valor: se não
estiver legível, deixe vazio e marque a confiança como baixa. Escolha a categoria
de despesa que melhor descreve a compra."""

TIPOS = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "pdf": "application/pdf"}


def bloco_do_arquivo(nome: str, dados: bytes) -> dict:
    tipo = TIPOS[nome.rsplit(".", 1)[-1].lower()]
    fonte = {"type": "base64", "media_type": tipo, "data": base64.standard_b64encode(dados).decode()}
    return {"type": "document" if tipo == "application/pdf" else "image", "source": fonte}


def ler_nota(nome: str, dados: bytes) -> Nota:
    conteudo = [bloco_do_arquivo(nome, dados), {"type": "text", "text": "Extraia os dados desta nota."}]
    return extrair(conteudo, Nota, INSTRUCOES)


def notas_em_csv(notas: dict[str, Nota]) -> str:
    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=";")
    escritor.writerow(["arquivo", "data", "emitente", "cnpj", "numero", "categoria", "pagamento", "valor_total", "confianca"])
    for arquivo, n in notas.items():
        escritor.writerow([arquivo, n.data_emissao, n.emitente, n.cnpj, n.numero, n.categoria,
                           n.forma_pagamento, f"{n.valor_total:.2f}".replace(".", ","), n.confianca])
    return saida.getvalue()


def reais(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


st.set_page_config(page_title="Leitor de Notas Fiscais com IA", page_icon="🧾", layout="wide")
st.title("🧾 Leitor de Notas Fiscais com IA")
st.caption("Envie fotos ou PDFs de notas e cupons. A IA lê cada um e monta a planilha de despesas.")

arquivos = st.file_uploader("Notas fiscais", type=list(TIPOS), accept_multiple_files=True)

if st.button("Ler notas", type="primary", disabled=not arquivos):
    notas: dict[str, Nota] = {}
    progresso = st.progress(0.0)
    for i, arq in enumerate(arquivos, start=1):
        try:
            notas[arq.name] = ler_nota(arq.name, arq.getvalue())
        except ErroIA as e:
            st.warning(f"{arq.name}: {e}")
        progresso.progress(i / len(arquivos), text=f"{i} de {len(arquivos)}")
    st.session_state["notas"] = notas

notas: dict[str, Nota] = st.session_state.get("notas", {})
if notas:
    total = sum(n.valor_total for n in notas.values())
    c1, c2, c3 = st.columns(3)
    c1.metric("Notas lidas", len(notas))
    c2.metric("Total", reais(total))
    c3.metric("Precisam de revisão", sum(n.confianca == "baixa" for n in notas.values()))

    st.markdown("### Lançamentos")
    st.dataframe(
        [{"arquivo": a, "data": n.data_emissao, "emitente": n.emitente, "categoria": n.categoria,
          "total": reais(n.valor_total), "confiança": n.confianca} for a, n in notas.items()],
        use_container_width=True, hide_index=True,
    )

    por_categoria: dict[str, float] = {}
    for n in notas.values():
        por_categoria[n.categoria] = por_categoria.get(n.categoria, 0) + n.valor_total
    st.markdown("### Gasto por categoria")
    st.bar_chart(por_categoria, horizontal=True)

    st.markdown("### Itens por nota")
    for arquivo, n in notas.items():
        with st.expander(f"{n.emitente} · {reais(n.valor_total)} · {arquivo}"):
            st.dataframe([i.model_dump() for i in n.itens], use_container_width=True, hide_index=True)

    st.download_button("Baixar planilha (.csv)", notas_em_csv(notas), "notas.csv", "text/csv")
