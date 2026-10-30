# 🧾 Leitor de Notas Fiscais com IA

Recebe **fotos ou PDFs** de notas fiscais e cupons (NF-e, NFC-e, cupom, recibo) e devolve uma **planilha de despesas pronta**: emitente, CNPJ, data, itens, valor total, forma de pagamento e **categoria da despesa**, além de um aviso nas notas que precisam de revisão humana.

## O problema

Reembolso de despesas e lançamento contábil ainda são feitos digitando nota por nota. Um lote de 50 cupons leva horas de digitação, com erros de valor e de data.

## Como a IA resolve

- O **Claude** (modelo com visão) lê a imagem ou o PDF direto, sem OCR separado.
- A resposta é **validada por um esquema Pydantic** (saída estruturada), com categoria de despesa restrita a uma lista fixa.
- O modelo informa a **confiança** da leitura. Notas borradas ou cortadas são marcadas para revisão em vez de terem valores inventados.
- Mostra o total e o gasto por categoria, e exporta **CSV com `;`** (abre direto no Excel em português).

## Rodando

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave"
streamlit run app.py
```

Tire uma foto de qualquer cupom fiscal e envie. Dá pra mandar vários arquivos de uma vez.

## Estrutura

| Arquivo | O que faz |
|---|---|
| `app.py` | Interface Streamlit, esquema `Nota`/`Item`, gráfico e exportação |
| `ia.py` | Chamada ao Claude com saída estruturada e tratamento de erros |

## Stack

Python · Streamlit · Anthropic SDK (Claude com visão, structured outputs) · Pydantic

## Próximos passos

- Validar o CNPJ (dígito verificador) e consultar a chave de acesso da NF-e na SEFAZ
- Enviar os lançamentos direto para uma planilha Google ou para o ERP
