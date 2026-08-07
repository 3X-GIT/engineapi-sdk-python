"""Engine API — Client principal."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from engineapi.http_client import HttpClient
from engineapi.clients.nfe import NfeClient
from engineapi.clients.companies import CompaniesClient

# A superfície pública deste SDK cobre NFe, NFCe e NFSe. Não existe
# `EngineApiClient.dfe`; a regressão que garante isso está em
# tests/test_client.py.


class EngineApiClient:
    """SDK Python oficial da Engine API.

    Uso básico::

        from engineapi import EngineApiClient

        client = EngineApiClient(
            base_url="https://api.engineapi.com.br",
            api_key="ek_live_xxx",
        )

        # Emitir NFe
        nfe = client.nfe.emitir({...})

    Args:
        base_url: URL base da API (ex: ``https://api.engineapi.com.br``).
        api_key: API Key para autenticação server-to-server.
        token: JWT Token (gerado via login).
        timeout: Timeout em segundos (default: 30).
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 30.0,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        """``transport`` é só para teste (injeta ``httpx.MockTransport`` nos
        testes de contrato de ``tests/test_client.py``), sem bater na rede
        real. Ausente = comportamento normal."""
        self._http = HttpClient(
            base_url=base_url,
            api_key=api_key,
            token=token,
            timeout=timeout,
            transport=transport,
        )

        self.nfe = NfeClient(self._http)
        """Módulo NFe — Emissão, consulta, cancelamento."""

        self.companies = CompaniesClient(self._http)
        """Módulo Empresas — Cadastro e certificados."""

    def login(self, email: str, password: str) -> dict[str, Any]:
        """Login com email/senha, guardando o JWT para as chamadas seguintes.

        Toda resposta de sucesso da API vem envelopada em
        ``{data: {...}, meta: {...}}``: o ``access_token`` fica em
        ``data.access_token``. Este método desembrulha o envelope, guarda o
        token no cliente e devolve o conteúdo de ``data``, para que a
        chamada seguinte já saia autenticada sem nenhum passo extra.

        Returns:
            Dict com ``access_token`` e ``user`` (``id``, ``email``,
            ``name``, ``partnerId``, ``role``).
        """
        envelope = self._http.post("/auth/login", json={"email": email, "password": password})
        data = envelope.get("data") if isinstance(envelope, dict) else None
        if isinstance(data, dict) and "access_token" in data:
            self._http.set_token(data["access_token"])
        return data if data is not None else envelope

    def regenerate_api_key(self) -> dict[str, Any]:
        """Regenerar API Key."""
        return self._http.post("/auth/api-keys/regenerate")

    def api_key_info(self) -> dict[str, Any]:
        """Info da API Key atual."""
        return self._http.get("/auth/api-keys/info")

    def health(self) -> dict[str, Any]:
        """Verifica se a API está online (GET /health, sem /v1)."""
        resp = httpx.get(f"{self._http._base_url}/health", timeout=10)
        return resp.json()

    def close(self) -> None:
        """Fecha a conexão HTTP."""
        self._http.close()

    def __enter__(self) -> EngineApiClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
