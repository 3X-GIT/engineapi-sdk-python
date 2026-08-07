"""Engine API — HTTP Client wrapper (httpx)."""

from __future__ import annotations

from typing import Any, Optional

import httpx

from engineapi.errors import EngineApiError


class HttpClient:
    """Cliente HTTP para comunicação com a Engine API.

    Suporta autenticação via API Key (X-API-Key) e/ou JWT (Bearer token).
    Todas as requisições são prefixadas com ``/v1``.
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
        testes de contrato, sem subir servidor nem bater na rede real).
        Ausente = comportamento normal do ``httpx.Client``.
        """
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._token = token
        self._timeout = timeout
        self._client = httpx.Client(
            base_url=f"{self._base_url}/v1",
            timeout=timeout,
            headers=self._build_headers(),
            transport=transport,
        )

    def set_token(self, token: str) -> None:
        """Define o JWT token para requisições autenticadas."""
        self._token = token
        self._client.headers.update(self._build_headers())

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    @staticmethod
    def _extract_error_message(body: Any, fallback: str = "Request failed") -> str:
        """Extrai uma mensagem de erro legível do corpo JSON de uma resposta
        de erro da engineAPI.

        O corpo de erro segue a RFC 7807 e vem aninhado em ``error``:
        ``{error: {type, title, status, detail, erros, instance, requestId,
        timestamp}}``.

        Ordem de extração: ``error.detail``, depois ``error.title``, depois
        ``message``/``detail`` no topo (compatibilidade com corpos fora do
        formato RFC 7807, como o de um proxy na frente da API) e por fim o
        ``fallback`` se nada bater.
        """
        if isinstance(body, dict):
            err = body.get("error")
            if isinstance(err, dict):
                detail = err.get("detail")
                if isinstance(detail, str) and detail:
                    return detail
                title = err.get("title")
                if isinstance(title, str) and title:
                    return title

            message = body.get("message")
            if isinstance(message, str) and message:
                return message
            detail = body.get("detail")
            if isinstance(detail, str) and detail:
                return detail

        return fallback

    def _handle_response(self, response: httpx.Response) -> Any:
        """Processa a resposta HTTP, levantando EngineApiError em caso de erro."""
        if response.status_code >= 400:
            try:
                body = response.json()
            except Exception:
                body = {"detail": response.text}
            message = self._extract_error_message(body)
            raise EngineApiError(
                message=message,
                status_code=response.status_code,
                response=body,
            )
        try:
            return response.json()
        except Exception:
            return response.text

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """GET request."""
        resp = self._client.get(path, params=params)
        return self._handle_response(resp)

    def post(self, path: str, json: Optional[Any] = None) -> Any:
        """POST request."""
        resp = self._client.post(path, json=json)
        return self._handle_response(resp)

    def post_multipart(
        self,
        path: str,
        files: dict[str, Any],
        data: Optional[dict[str, Any]] = None,
    ) -> Any:
        """POST ``multipart/form-data``.

        Usado por ``CompaniesClient.upload_certificado()``: o endpoint de
        certificado recebe o arquivo em multipart, não em JSON.

        Não reusa ``self._client.post(path, files=..., data=...)`` de
        propósito. O cliente carrega ``Content-Type: application/json`` fixo
        nos headers padrão (usado por todas as outras chamadas) e o
        ``httpx.Client`` dá prioridade a esse header sobre o
        ``multipart/form-data; boundary=...`` que ele mesmo calcularia para o
        corpo: o corpo sairia multipart de verdade, mas o header anunciaria
        JSON, e qualquer parser RFC 7578 rejeitaria ou leria o corpo errado.
        Por isso monta o ``httpx.Request`` como objeto solto (sem herdar os
        headers padrão) e só então empresta os headers de autenticação antes
        de enviar via ``self._client.send()``.
        """
        url = self._client.base_url.join(path.lstrip("/"))
        request = httpx.Request("POST", url, files=files, data=data)
        request.headers["Accept"] = "application/json"
        if self._api_key:
            request.headers["X-API-Key"] = self._api_key
        if self._token:
            request.headers["Authorization"] = f"Bearer {self._token}"
        resp = self._client.send(request)
        return self._handle_response(resp)

    def put(self, path: str, json: Optional[Any] = None) -> Any:
        """PUT request."""
        resp = self._client.put(path, json=json)
        return self._handle_response(resp)

    def patch(self, path: str, json: Optional[Any] = None) -> Any:
        """PATCH request."""
        resp = self._client.patch(path, json=json)
        return self._handle_response(resp)

    def delete(self, path: str) -> Any:
        """DELETE request."""
        resp = self._client.delete(path)
        return self._handle_response(resp)

    def download(self, path: str) -> bytes:
        """Download binário (PDF, XML)."""
        resp = self._client.get(path)
        if resp.status_code >= 400:
            raise EngineApiError(
                message=f"Download failed: {resp.status_code}",
                status_code=resp.status_code,
            )
        return resp.content

    def close(self) -> None:
        """Fecha o client HTTP."""
        self._client.close()
