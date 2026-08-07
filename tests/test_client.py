"""Testes do SDK Python — Engine API."""

import importlib
import json

import httpx
import pytest
from unittest.mock import MagicMock, patch

from engineapi import EngineApiClient, EngineApiError
from engineapi.clients.companies import CompaniesClient
from engineapi.http_client import HttpClient


# ========================================
# EngineApiError
# ========================================


class TestEngineApiError:
    def test_basic_error(self):
        err = EngineApiError("Not found", 404)
        assert str(err) == "Not found"
        assert err.status_code == 404
        assert err.is_not_found is True
        assert err.is_unauthorized is False

    def test_unauthorized(self):
        err = EngineApiError("Invalid token", 401)
        assert err.is_unauthorized is True
        assert err.is_not_found is False

    def test_rate_limited(self):
        err = EngineApiError("Too many requests", 429)
        assert err.is_rate_limited is True

    def test_validation_error(self):
        err = EngineApiError("Bad request", 400, {"errors": [{"field": "cnpj"}]})
        assert err.is_validation_error is True
        assert err.response == {"errors": [{"field": "cnpj"}]}

    def test_server_error(self):
        err = EngineApiError("Internal", 500)
        assert err.is_server_error is True

    def test_repr(self):
        err = EngineApiError("Oops", 503)
        assert "503" in repr(err)


# ========================================
# EngineApiClient
# ========================================


class TestEngineApiClient:
    def test_creates_sub_clients(self):
        client = EngineApiClient(base_url="http://api.example.test")
        assert hasattr(client, "nfe")
        assert hasattr(client, "companies")
        # A superfície pública cobre NFe, NFCe e NFSe (ver TestDfeRemoved).
        assert not hasattr(client, "dfe")
        client.close()

    def test_context_manager(self):
        with EngineApiClient(base_url="http://api.example.test") as client:
            assert client.nfe is not None

    def test_login_desembrulha_envelope_e_seta_token(self):
        """A resposta de login traz `{access_token, user}` dentro do envelope
        `{data, meta}` de toda resposta de sucesso da API. Este teste usa mock
        de método (contrato leve); `TestLoginContract` abaixo prova o mesmo no
        fio, com `httpx.MockTransport`."""
        client = EngineApiClient(base_url="http://api.example.test")
        envelope = {
            "data": {
                "access_token": "jwt_token_123",
                "user": {
                    "id": "u1",
                    "email": "test@test.com",
                    "name": "Dev Parceiro",
                    "partnerId": "p1",
                    "role": "ADMIN",
                },
            },
            "meta": {"requestId": "req_abc123", "timestamp": "2026-08-04T12:00:00.000Z"},
        }

        with patch.object(client._http, "post", return_value=envelope) as mock_post, patch.object(
            client._http, "set_token"
        ) as mock_set_token:
            result = client.login("test@test.com", "pass123")

        mock_post.assert_called_once_with(
            "/auth/login", json={"email": "test@test.com", "password": "pass123"}
        )
        # Desembrulhado: sem `data`/`meta` por fora, direto access_token/user.
        assert "data" not in result
        assert "meta" not in result
        assert result["access_token"] == "jwt_token_123"
        assert result["user"]["partnerId"] == "p1"
        assert "partner" not in result
        mock_set_token.assert_called_once_with("jwt_token_123")
        client.close()


# ========================================
# NfeClient
# ========================================


class TestNfeClient:
    def setup_method(self):
        self.client = EngineApiClient(base_url="http://api.example.test")
        self.mock_http = MagicMock(spec=HttpClient)
        self.client.nfe._http = self.mock_http

    def teardown_method(self):
        self.client.close()

    def test_emitir(self):
        self.mock_http.post.return_value = {"id": "nfe-1", "status": "AUTHORIZED"}
        result = self.client.nfe.emitir({"emitente": {"issuerId": "123"}})
        self.mock_http.post.assert_called_once_with("/nfe", json={"emitente": {"issuerId": "123"}})
        assert result["status"] == "AUTHORIZED"

    def test_listar(self):
        self.mock_http.get.return_value = {"data": [], "pagination": {}}
        result = self.client.nfe.listar(page=2, limit=10)
        self.mock_http.get.assert_called_once_with(
            "/nfe", params={"page": 2, "limit": 10}
        )

    def test_cancelar(self):
        self.mock_http.post.return_value = {"success": True}
        self.client.nfe.cancelar("chave123", "Erro de digitação")
        self.mock_http.post.assert_called_once_with(
            "/nfe/chave123/cancelar",
            json={"justificativa": "Erro de digitação"},
        )

    def test_download_pdf(self):
        self.mock_http.download.return_value = b"%PDF-1.4..."
        result = self.client.nfe.download_pdf("chave123")
        assert result == b"%PDF-1.4..."
        self.mock_http.download.assert_called_once_with("/nfe/pdf/chave123")

    def test_status(self):
        self.mock_http.get.return_value = {"status": "online"}
        result = self.client.nfe.status()
        assert result["status"] == "online"


# ========================================
# CompaniesClient
# ========================================


class TestCompaniesClient:
    """Cadastro de empresas emissoras: `/companies`."""

    def setup_method(self):
        self.client = EngineApiClient(base_url="http://api.example.test")
        self.mock_http = MagicMock(spec=HttpClient)
        self.client.companies._http = self.mock_http

    def teardown_method(self):
        self.client.close()

    def test_criar(self):
        self.mock_http.post.return_value = {"id": "comp-1"}
        result = self.client.companies.criar({"cnpj": "99888777000100"})
        self.mock_http.post.assert_called_once_with(
            "/companies", json={"cnpj": "99888777000100"}
        )
        assert result["id"] == "comp-1"

    def test_listar(self):
        self.mock_http.get.return_value = {"data": []}
        self.client.companies.listar()
        self.mock_http.get.assert_called_once_with("/companies")

    def test_buscar(self):
        self.mock_http.get.return_value = {"id": "comp-1"}
        self.client.companies.buscar("comp-1")
        self.mock_http.get.assert_called_once_with("/companies/comp-1")

    def test_consultar_cnpj(self):
        self.mock_http.get.return_value = {"razaoSocial": "Empresa XPTO"}
        result = self.client.companies.consultar_cnpj("99888777000100")
        self.mock_http.get.assert_called_once_with(
            "/companies/consult/99888777000100"
        )
        assert result["razaoSocial"] == "Empresa XPTO"

    def test_upload_certificado(self):
        """Certificado A1 vai por multipart, com os campos `file` e
        `password`."""
        self.mock_http.post_multipart.return_value = {"success": True}
        self.client.companies.upload_certificado(
            "comp-1", b"conteudo-fake-do-pfx", "senha123"
        )
        self.mock_http.post_multipart.assert_called_once_with(
            "/companies/comp-1/certificate",
            files={
                "file": ("certificado.pfx", b"conteudo-fake-do-pfx", "application/x-pkcs12")
            },
            data={"password": "senha123"},
        )

    def test_upload_certificado_retrocompat_base64(self):
        """Assinatura antiga do SDK 1.0.0 (string base64) continua funcionando
        com `base64_encoded=True` — decodifica antes de montar o multipart."""
        import base64

        self.mock_http.post_multipart.return_value = {"success": True}
        conteudo_b64 = base64.b64encode(b"conteudo-fake-do-pfx").decode()
        self.client.companies.upload_certificado(
            "comp-1", conteudo_b64, "senha123", base64_encoded=True
        )
        files_arg = self.mock_http.post_multipart.call_args.kwargs["files"]
        assert files_arg["file"][1] == b"conteudo-fake-do-pfx"


class TestCompaniesContract:
    """Prova de contrato no fio (sem mock de método): sobe um
    `httpx.MockTransport` real e captura o request que o SDK monta de
    verdade (método, caminho, headers e corpo)."""

    def test_criar_bate_em_post_companies(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["method"] = request.method
            captured["path"] = request.url.path
            captured["headers"] = request.headers
            captured["body"] = json.loads(request.content)
            return httpx.Response(
                201, json={"success": True, "data": {"id": "empresa-1"}}
            )

        http = HttpClient(
            base_url="http://example.test",
            token="jwt-fake",
            transport=httpx.MockTransport(handler),
        )
        companies = CompaniesClient(http)
        result = companies.criar(
            {"cnpj": "99888777000100", "name": "Minha Empresa LTDA"}
        )

        assert captured["method"] == "POST"
        assert captured["path"] == "/v1/companies"
        assert captured["headers"]["authorization"] == "Bearer jwt-fake"
        assert captured["body"]["name"] == "Minha Empresa LTDA"
        assert result["data"]["id"] == "empresa-1"

    def test_upload_certificado_manda_multipart_de_verdade(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["path"] = request.url.path
            captured["content_type"] = request.headers.get("content-type", "")
            captured["body"] = request.content
            return httpx.Response(200, json={"success": True})

        http = HttpClient(
            base_url="http://example.test",
            token="jwt-fake",
            transport=httpx.MockTransport(handler),
        )
        companies = CompaniesClient(http)
        companies.upload_certificado(
            "empresa-1", b"conteudo-fake-do-pfx", "senha123"
        )

        assert captured["path"] == "/v1/companies/empresa-1/certificate"
        assert captured["content_type"].startswith("multipart/form-data; boundary=")
        assert b'name="password"' in captured["body"]
        assert b"senha123" in captured["body"]
        assert b'name="file"; filename="certificado.pfx"' in captured["body"]
        assert b"conteudo-fake-do-pfx" in captured["body"]


class TestDfeRemoved:
    """A superfície pública deste SDK cobre NFe, NFCe e NFSe. Regressão:
    garante que ninguém reintroduz `client.dfe` ou `engineapi.clients.dfe`
    sem ser deliberado."""

    def test_client_nao_tem_atributo_dfe(self):
        client = EngineApiClient(base_url="http://api.example.test")
        assert not hasattr(client, "dfe")
        client.close()

    def test_modulo_dfe_nao_existe_mais(self):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("engineapi.clients.dfe")

    def test_tipos_dfe_nao_existem_mais_em_engineapi_types(self):
        """`ConsultaDfeParams`, `ManifestarParams` e `DfeDocument` não fazem
        parte do contrato deste SDK e não podem voltar a `types.py` como tipos
        órfãos, prometendo um contrato que não existe. Import dinâmico (e não
        `from ... import X`, que quebraria a COLETA do teste em vez do teste em
        si) somado a `hasattr`."""
        tipos = importlib.import_module("engineapi.types")
        for nome in ("ConsultaDfeParams", "ManifestarParams", "DfeDocument"):
            assert not hasattr(tipos, nome), (
                f"engineapi.types.{nome} não faz parte do contrato deste "
                "SDK. Reintroduzido sem ser deliberado?"
            )


class TestLoginContract:
    """`EngineApiClient.login()`: prova de contrato no fio (sem mock de
    método). Um `httpx.MockTransport` real captura o request que o SDK monta e
    a resposta que ele recebe, garantindo que o envelope `{data, meta}` é
    desembrulhado e o token guardado."""

    def test_login_desembrulha_envelope_e_seta_token_para_chamada_seguinte(self):
        calls: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(request)
            if request.url.path == "/v1/auth/login":
                # Formato real da resposta de login: `user` dentro do
                # envelope `{data, meta}`.
                return httpx.Response(
                    200,
                    json={
                        "data": {
                            "access_token": "jwt.fake.token",
                            "user": {
                                "id": "u1",
                                "email": "dev@parceiro.com.br",
                                "name": "Dev Parceiro",
                                "partnerId": "p1",
                                "role": "ADMIN",
                            },
                        },
                        "meta": {
                            "requestId": "req_abc123",
                            "timestamp": "2026-08-04T12:00:00.000Z",
                        },
                    },
                )
            # 2ª chamada: companies.listar(), só para capturar o header
            # Authorization que ela manda depois do login.
            return httpx.Response(200, json={"success": True, "data": []})

        client = EngineApiClient(
            base_url="http://example.test", transport=httpx.MockTransport(handler)
        )

        result = client.login("dev@parceiro.com.br", "senha123")

        assert "data" not in result
        assert "meta" not in result
        assert result["access_token"] == "jwt.fake.token"
        assert result["user"]["email"] == "dev@parceiro.com.br"
        assert result["user"]["partnerId"] == "p1"
        assert "partner" not in result

        # set_token() foi chamado de verdade: a PRÓXIMA chamada (JWT-only por
        # padrão) já sai com o Bearer certo, sem o consumidor fazer nada.
        client.companies.listar()
        assert len(calls) == 2
        assert calls[1].headers["authorization"] == "Bearer jwt.fake.token"
        client.close()

    def test_login_401_passa_pelo_tratamento_de_erro_existente(self):
        def handler(request: httpx.Request) -> httpx.Response:
            # Formato real de erro (RFC 7807): o detail fica ANINHADO em
            # `error.detail`, não no topo do corpo.
            return httpx.Response(
                401,
                json={
                    "error": {
                        "type": "https://engineapi.com.br/errors/UNAUTHORIZED",
                        "title": "Não Autorizado",
                        "status": 401,
                        "detail": "Credenciais inválidas",
                        "requestId": "req_xyz789",
                        "timestamp": "2026-08-04T12:00:00.000Z",
                    }
                },
            )

        client = EngineApiClient(
            base_url="http://example.test", transport=httpx.MockTransport(handler)
        )

        # O 401 propaga íntegro pelo tratamento de erro existente
        # (HttpClient._handle_response() -> EngineApiError) — garante que
        # login() com credencial errada nunca retorna silenciosamente um
        # dict sem token, sempre levanta.
        with pytest.raises(EngineApiError) as exc_info:
            client.login("dev@parceiro.com.br", "senha-errada")

        assert exc_info.value.status_code == 401
        assert exc_info.value.is_unauthorized is True
        # A mensagem sai de `error.detail` (RFC 7807 aninhado), não do
        # fallback genérico (ver TestErrorMessageExtraction).
        assert str(exc_info.value) == "Credenciais inválidas"
        client.close()


class TestErrorMessageExtraction:
    """Extração da mensagem curta de `EngineApiError`. O corpo de erro da
    engineAPI segue a RFC 7807: `{error: {type, title, status, detail, ...}}`,
    com `detail` e `message` aninhados, nunca no topo do corpo."""

    def _client_with_mocked_response(self, status: int, body) -> EngineApiClient:
        def handler(request: httpx.Request) -> httpx.Response:
            if isinstance(body, (bytes, str)):
                return httpx.Response(status, content=body)
            return httpx.Response(status, json=body)

        return EngineApiClient(
            base_url="http://example.test", transport=httpx.MockTransport(handler)
        )

    def test_corpo_rfc7807_real_vira_mensagem_do_detail(self):
        client = self._client_with_mocked_response(
            401,
            {
                "error": {
                    "type": "https://engineapi.com.br/errors/UNAUTHORIZED",
                    "title": "Não Autorizado",
                    "status": 401,
                    "detail": "Credenciais inválidas",
                }
            },
        )
        with pytest.raises(EngineApiError) as exc_info:
            client.companies.listar()
        assert str(exc_info.value) == "Credenciais inválidas"
        assert exc_info.value.status_code == 401
        client.close()

    def test_corpo_rfc7807_sem_detail_usa_o_title(self):
        client = self._client_with_mocked_response(
            403,
            {
                "error": {
                    "type": "https://engineapi.com.br/errors/FORBIDDEN",
                    "title": "Acesso Negado",
                    "status": 403,
                    # sem `detail`
                }
            },
        )
        with pytest.raises(EngineApiError) as exc_info:
            client.companies.listar()
        assert str(exc_info.value) == "Acesso Negado"
        client.close()

    def test_corpo_fora_do_shape_rfc7807_cai_no_fallback_de_topo(self):
        """Compatibilidade: corpo com `message` no topo (fora do formato RFC
        7807, como o de um proxy ou gateway na frente da API) continua
        funcionando."""
        client = self._client_with_mocked_response(400, {"message": "Erro genérico de gateway"})
        with pytest.raises(EngineApiError) as exc_info:
            client.companies.listar()
        assert str(exc_info.value) == "Erro genérico de gateway"
        client.close()

    def test_corpo_totalmente_fora_do_shape_nao_quebra_cai_no_fallback_generico(self):
        """Corpo de erro sem NENHUM campo reconhecível (nem `error.detail`,
        nem `message`/`detail` de topo) não pode quebrar o SDK — cai no
        fallback ("Request failed"), nunca uma exceção não tratada."""
        client = self._client_with_mocked_response(500, {"algumCampoQualquer": "x"})
        with pytest.raises(EngineApiError) as exc_info:
            client.companies.listar()
        assert exc_info.value.status_code == 500
        assert isinstance(str(exc_info.value), str)
        assert str(exc_info.value) != ""
        client.close()

    def test_corpo_nao_json_nao_quebra_cai_no_fallback(self):
        """Corpo de erro que nem chega a ser JSON válido (como o 502 de um
        proxy devolvendo HTML) não pode quebrar `_extract_error_message` com
        TypeError."""
        client = self._client_with_mocked_response(502, "<html>Bad Gateway</html>")
        with pytest.raises(EngineApiError) as exc_info:
            client.companies.listar()
        assert exc_info.value.status_code == 502
        assert isinstance(str(exc_info.value), str)
        assert str(exc_info.value) != ""
        client.close()
