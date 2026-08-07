"""Engine API — Companies Client.

Cadastro de empresas emissoras: ``/companies``. O upload do certificado
digital A1 é enviado em ``multipart/form-data`` (campo ``file`` mais o campo
``password``).
"""

from __future__ import annotations

import base64
from typing import Any, Union

from engineapi.http_client import HttpClient


class CompaniesClient:
    """Módulo Empresas — Cadastro, certificados e consulta CNPJ."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def criar(self, params: dict[str, Any]) -> dict[str, Any]:
        """Cadastrar nova empresa/emissor. Aceita JWT (``token``) ou API Key."""
        return self._http.post("/companies", json=params)

    def listar(self) -> dict[str, Any]:
        """Listar empresas/emissores do parceiro. Aceita JWT ou API Key."""
        return self._http.get("/companies")

    def buscar(self, company_id: str) -> dict[str, Any]:
        """Buscar empresa por ID. Aceita JWT ou API Key."""
        return self._http.get(f"/companies/{company_id}")

    def consultar_cnpj(self, cnpj: str) -> dict[str, Any]:
        """Consultar CNPJ na Receita Federal. Aceita JWT ou API Key."""
        return self._http.get(f"/companies/consult/{cnpj}")

    def upload_certificado(
        self,
        company_id: str,
        certificado: Union[bytes, str],
        senha: str,
        filename: str = "certificado.pfx",
        *,
        base64_encoded: bool = False,
    ) -> dict[str, Any]:
        """Upload certificado digital A1 (.pfx). Aceita JWT ou API Key.

        Envia ``multipart/form-data`` com os campos ``file`` e ``password``.

        Args:
            certificado: conteúdo binário do ``.pfx``. Passe ``bytes`` lidos
                de ``open(caminho, "rb").read()`` (recomendado).
            base64_encoded: ``True`` se ``certificado`` vier como string
                base64 (retrocompat com a assinatura antiga do SDK 1.0.0,
                que só aceitava base64). Default ``False`` — binário direto.
        """
        conteudo = base64.b64decode(certificado) if base64_encoded else certificado
        return self._http.post_multipart(
            f"/companies/{company_id}/certificate",
            files={"file": (filename, conteudo, "application/x-pkcs12")},
            data={"password": senha},
        )
