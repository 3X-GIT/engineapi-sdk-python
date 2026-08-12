"""Regressões dos shapes publicados do SDK (issue #583)."""

import pytest
from pydantic import ValidationError

from engineapi.types import (
    CreateCompanyParams,
    CreateNfceParams,
    CreateNfeParams,
    CreateNfseParams,
    LoginResponse,
)


def test_login_response_uses_partner_id_from_openapi():
    assert LoginResponse(access_token="jwt", partnerId="partner-1").partnerId == "partner-1"
    with pytest.raises(ValidationError):
        LoginResponse(access_token="jwt", partner={"id": "partner-1"})


def test_company_payload_is_flat_and_uses_contract_names():
    company = CreateCompanyParams(
        cnpj="99888777000100",
        name="Empresa Exemplo LTDA",
        address="Av. Goiás",
        city="Goiânia",
        state="GO",
    )
    assert company.model_dump(exclude_none=True)["name"] == "Empresa Exemplo LTDA"
    with pytest.raises(ValidationError):
        CreateCompanyParams(
            cnpj="99888777000100",
            razaoSocial="Empresa Exemplo LTDA",
            endereco={"logradouro": "Av. Goiás"},
        )


def test_nfe_uses_top_level_issuer_id_and_english_items():
    payload = CreateNfeParams(
        issuerId="issuer-1",
        destinatario={
            "cnpjCpf": "99888777000100",
            "nome": "Cliente Exemplo SA",
            "endereco": {
                "logradouro": "Av. Goiás",
                "numero": "500",
                "bairro": "Centro",
                "codigoMunicipio": "5208707",
                "municipio": "Goiânia",
                "uf": "GO",
                "cep": "74063010",
            },
        },
        items=[{
            "codigo": "PROD001",
            "descricao": "Produto teste",
            "ncm": "84713012",
            "cfop": "5102",
            "unidade": "UN",
            "quantidade": 1,
            "valorUnitario": 100,
        }],
        pagamentos=[{"forma": "01", "valor": 100}],
    )
    assert payload.items[0].codigo == "PROD001"
    with pytest.raises(ValidationError):
        CreateNfeParams(
            emitente={"issuerId": "issuer-1"},
            destinatario=payload.destinatario,
            itens=[],
        )


def test_nfce_and_nfse_expose_current_nested_shapes():
    nfce = CreateNfceParams(
        items=[{
            "codigo": "PROD001",
            "descricao": "Produto teste",
            "ncm": "84713012",
            "cfop": "5102",
            "unidade": "UN",
            "quantidade": 1,
            "valorUnitario": 100,
        }],
        pagamentos=[{"forma": "01", "valor": 100}],
        indPres=4,
    )
    assert nfce.indPres == 4

    nfse = CreateNfseParams(
        issuerId="issuer-1",
        tomador={
            "cnpjCpf": "99888777000100",
            "razaoSocial": "Tomador Exemplo",
            "endereco": {
                "logradouro": "Av. Goiás",
                "numero": "500",
                "bairro": "Centro",
                "codigoMunicipio": "5208707",
                "uf": "GO",
                "cep": "74063010",
            },
        },
        servico={
            "codigoMunicipio": "5208707",
            "discriminacao": "Consultoria",
            "valorServicos": 100,
        },
    )
    assert nfse.servico.codigoMunicipio == "5208707"
