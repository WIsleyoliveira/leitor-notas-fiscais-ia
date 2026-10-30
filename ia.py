"""Chamada única ao Claude com saída estruturada (validada por Pydantic)."""

import os
from typing import TypeVar

import anthropic
from pydantic import BaseModel

MODELO = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")
T = TypeVar("T", bound=BaseModel)

_client = anthropic.Anthropic()  # lê ANTHROPIC_API_KEY do ambiente


class ErroIA(Exception):
    pass


def extrair(conteudo: str | list, esquema: type[T], instrucoes: str) -> T:
    """Envia o conteúdo ao modelo e devolve um objeto do `esquema` já validado."""
    try:
        resposta = _client.beta.messages.parse(
            model=MODELO,
            max_tokens=16000,
            system=instrucoes,
            messages=[{"role": "user", "content": conteudo}],
            output_format=esquema,
            output_config={"effort": "low"},
            # se o modelo recusar, a API tenta outro modelo na mesma chamada
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.AuthenticationError as e:
        raise ErroIA("Chave da API inválida ou ausente (ANTHROPIC_API_KEY).") from e
    except anthropic.RateLimitError as e:
        raise ErroIA("Limite de requisições atingido. Tente de novo em instantes.") from e
    except anthropic.APIStatusError as e:
        raise ErroIA(f"Erro da API ({e.status_code}): {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise ErroIA("Sem conexão com a API da Anthropic.") from e

    if resposta.stop_reason == "refusal":
        raise ErroIA("O modelo recusou processar este conteúdo.")
    if resposta.stop_reason == "max_tokens" or resposta.parsed_output is None:
        raise ErroIA("A resposta veio incompleta. Tente com um conteúdo menor.")
    return resposta.parsed_output
