# 🧾 Leitor de Notas Fiscais com IA

Recebe **fotos ou PDFs** de notas fiscais e cupons (NF-e, NFC-e, cupom, recibo) e devolve uma **planilha de despesas pronta**: emitente, CNPJ, data, itens, valor total, forma de pagamento e **categoria da despesa**, além de um aviso nas notas que precisam de revisão humana.

## O problema

Reembolso de despesas e lançamento contábil ainda são feitos digitando nota por nota. Um lote de 50 cupons leva horas de digitação, com erros de valor e de data.

## Como a IA resolve

- Fotos vão para um modelo **local com visão** (`gemma3:4b` no Ollama), que lê a imagem direto, sem OCR separado. PDFs de NF-e têm o texto extraído com `pypdf` e vão para o `llama3.1:8b`.
- A resposta é **validada por um esquema Pydantic** (o Ollama gera direto no formato do esquema), com categoria de despesa restrita a uma lista fixa.
- O modelo informa a **confiança** da leitura. Notas borradas ou cortadas são marcadas para revisão em vez de terem valores inventados.
- Mostra o total e o gasto por categoria, e exporta **CSV com `;`** (abre direto no Excel em português).

## Rodando

Precisa do [Ollama](https://ollama.com) instalado e aberto.

```bash
ollama pull llama3.1:8b   # notas em PDF
ollama pull gemma3:4b     # fotos de notas (modelo com visão)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Roda **100% local**: nenhuma nota sai da sua máquina e não precisa de chave de API. Os modelos podem ser trocados com `OLLAMA_MODEL` (texto) e `OLLAMA_MODEL_VISAO` (imagem).

Tire uma foto de qualquer cupom fiscal e envie. Dá pra mandar vários arquivos de uma vez.

## Estrutura

| Arquivo | O que faz |
|---|---|
| `app.py` | Interface Streamlit, esquema `Nota`/`Item`, leitura do PDF, gráfico e exportação |
| `ia.py` | Chamada ao Ollama com saída estruturada e tratamento de erros |

## Stack

Python · Streamlit · Ollama (Gemma 3 com visão + Llama 3.1, local) · pypdf · Pydantic

## Próximos passos

- Validar o CNPJ (dígito verificador) e consultar a chave de acesso da NF-e na SEFAZ
- Enviar os lançamentos direto para uma planilha Google ou para o ERP
