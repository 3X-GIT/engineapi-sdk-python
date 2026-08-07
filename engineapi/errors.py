"""Engine API — Exceções customizadas."""

from __future__ import annotations

from typing import Any, Optional


class EngineApiError(Exception):
    """Erro retornado pela Engine API.

    Attributes:
        message: Mensagem de erro.
        status_code: HTTP status code.
        response: Corpo da resposta (dict) quando disponível.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response

    @property
    def is_not_found(self) -> bool:
        return self.status_code == 404

    @property
    def is_unauthorized(self) -> bool:
        return self.status_code == 401

    @property
    def is_rate_limited(self) -> bool:
        return self.status_code == 429

    @property
    def is_validation_error(self) -> bool:
        return self.status_code == 400

    @property
    def is_server_error(self) -> bool:
        return self.status_code >= 500

    def __repr__(self) -> str:
        return f"EngineApiError(status_code={self.status_code}, message='{self}')"
