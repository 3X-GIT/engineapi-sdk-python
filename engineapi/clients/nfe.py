"""Engine API — NFe Client."""

from __future__ import annotations

from typing import Any, Optional

from engineapi.http_client import HttpClient


class NfeClient:
    """Módulo NFe — Emissão, consulta, cancelamento, CC-e, DANFE e XML."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def emitir(self, params: dict[str, Any]) -> dict[str, Any]:
        """Emitir NFe (Modelo 55)."""
        return self._http.post("/nfe", json=params)

    def listar(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        issuer_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        """Listar NFes com paginação e filtros."""
        query: dict[str, Any] = {"page": page, "limit": limit}
        if issuer_id:
            query["issuerId"] = issuer_id
        if status:
            query["status"] = status
        return self._http.get("/nfe", params=query)

    def consultar(self, nfe_id: str) -> dict[str, Any]:
        """Consultar NFe por ID."""
        return self._http.get(f"/nfe/{nfe_id}")

    def cancelar(self, access_key: str, justificativa: str) -> dict[str, Any]:
        """Cancelar NFe."""
        return self._http.post(
            f"/nfe/{access_key}/cancelar",
            json={"justificativa": justificativa},
        )

    def carta_correcao(self, access_key: str, correcao: str) -> dict[str, Any]:
        """Enviar Carta de Correção (CC-e)."""
        return self._http.post(
            f"/nfe/{access_key}/carta-correcao",
            json={"correcao": correcao},
        )

    def download_pdf(self, access_key: str) -> bytes:
        """Download DANFE (PDF)."""
        return self._http.download(f"/nfe/pdf/{access_key}")

    def download_xml(self, access_key: str) -> bytes:
        """Download XML assinado."""
        return self._http.download(f"/nfe/xml/{access_key}")

    def download_cce_xml(self, access_key: str) -> bytes:
        """Download XML da CC-e."""
        return self._http.download(f"/nfe/cce/{access_key}/xml")

    def download_cce_pdf(self, access_key: str) -> bytes:
        """Download PDF da CC-e."""
        return self._http.download(f"/nfe/cce/{access_key}/pdf")

    def status(self) -> dict[str, Any]:
        """Status do serviço SEFAZ."""
        return self._http.get("/nfe/status")
