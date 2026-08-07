# engineAPI — SDK Python

SDK Python oficial da **engineAPI**, a infraestrutura fiscal para desenvolvedores: NF-e, NFC-e e NFS-e por uma única API REST.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org/)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green.svg)](LICENSE)

Documentação completa: [docs.engineapi.com.br](https://docs.engineapi.com.br)

## Instalação

```bash
pip install engine-api-python
```

Requer Python 3.9 ou superior.

## Autenticação

Duas formas, as duas suportadas pelo SDK:

- **API Key** (recomendada para servidor a servidor): header `X-API-Key`, sem expiração de sessão.
- **Login com email e senha**: devolve um JWT e já o guarda no cliente para as chamadas seguintes.

```python
from engineapi import EngineApiClient

client = EngineApiClient(
    base_url="https://api.engineapi.com.br",
    api_key="ek_live_sua_chave_aqui",
)

# Alternativa: login com email e senha
client = EngineApiClient(base_url="https://api.engineapi.com.br")
client.login("voce@suaempresa.com.br", "sua-senha")
```

## Exemplo mínimo: emitir uma NF-e

Toda resposta de sucesso vem envelopada em `{"data": ..., "meta": ...}`.

```python
from engineapi import EngineApiClient, EngineApiError

client = EngineApiClient(
    base_url="https://api.engineapi.com.br",
    api_key="ek_test_sua_chave_aqui",
)

try:
    resposta = client.nfe.emitir({
        "naturezaOperacao": "VENDA DE MERCADORIA",
        "idDest": 1,
        "indFinal": 1,
        "destinatario": {
            "cnpjCpf": "99888777000100",
            "nome": "Cliente Exemplo SA",
            "endereco": {
                "logradouro": "Av Goias", "numero": "500",
                "bairro": "Centro", "codigoMunicipio": "5208707",
                "municipio": "Goiania", "uf": "GO", "cep": "74063010",
            },
            "indicadorIE": 9,
        },
        "items": [{
            "codigo": "PROD001",
            "descricao": "Produto Teste",
            "ncm": "84713012",
            "cfop": "5102",
            "unidade": "UN",
            "quantidade": 2,
            "valorUnitario": 150.00,
            "icms": {"origem": 0, "csosn": "400"},
        }],
        "pagamentos": [{"forma": "01", "valor": 300.00}],
    })

    nota = resposta["data"]
    print("NF-e autorizada:", nota["accessKey"], nota["status"])

except EngineApiError as e:
    print(f"Erro {e.status_code}: {e}")
```

O campo dos itens é `items` e o das formas de pagamento é `pagamentos`. O contrato de emissão é estrito: campo desconhecido recebe `400` apontando o nome certo, antes de consumir numeração fiscal. A lista completa de campos está no [catálogo de campos da NF-e](https://docs.engineapi.com.br/api-reference/campos-nfe).

## Módulos

### NF-e

```python
client.nfe.emitir({...})
client.nfe.listar(page=1, limit=20, status="AUTHORIZED")
client.nfe.consultar("id-da-nota")
client.nfe.cancelar("chave_de_acesso", "Erro de digitacao no destinatario")
client.nfe.carta_correcao("chave_de_acesso", "Correcao do endereco de entrega")
client.nfe.status()

pdf = client.nfe.download_pdf("chave_de_acesso")
with open("danfe.pdf", "wb") as f:
    f.write(pdf)

xml = client.nfe.download_xml("chave_de_acesso")
```

### Empresas emissoras

Cadastro em `/companies`, com endereço em campos planos (`address`, `number`, `city`...).

```python
empresa = client.companies.criar({
    "cnpj": "99888777000100",
    "name": "Minha Empresa LTDA",
    "crt": 1,  # 1=Simples, 2=Simples com excesso de sublimite, 3=Regime Normal, 4=MEI
    "address": "Av Goias", "number": "500",
    "neighborhood": "Centro", "city": "Goiania",
    "state": "GO", "cep": "74063010", "ibgeCode": "5208707",
})

# Certificado digital A1 (.pfx), enviado em multipart/form-data
with open("certificado.pfx", "rb") as f:
    conteudo_pfx = f.read()
client.companies.upload_certificado(empresa["data"]["id"], conteudo_pfx, "senha-do-certificado")

client.companies.listar()
client.companies.buscar("id-da-empresa")
client.companies.consultar_cnpj("99888777000100")
```

## Context manager

```python
with EngineApiClient(base_url="https://api.engineapi.com.br", api_key="...") as client:
    client.nfe.emitir({...})
# a conexão HTTP fecha sozinha ao sair do bloco
```

## Tratamento de erros

Toda falha vira `EngineApiError`, com o status HTTP e o corpo da resposta preservados.

```python
from engineapi import EngineApiClient, EngineApiError

try:
    client.nfe.emitir({...})
except EngineApiError as e:
    print(f"Erro {e.status_code}: {e}")

    if e.is_validation_error:   # 400
        print("Dados inválidos:", e.response)
    elif e.is_unauthorized:     # 401
        print("Chave ou token inválido")
    elif e.is_rate_limited:     # 429
        print("Limite de requisições atingido")
    elif e.is_server_error:     # 5xx
        print("Falha do lado do servidor")
```

A mensagem curta sai do corpo de erro no formato RFC 7807 (`error.detail`), o mesmo texto que a referência da API documenta.

## Política de versão

Versionamento semântico (SemVer):

- **MAJOR**: mudança incompatível na API pública do SDK.
- **MINOR**: recurso novo mantendo compatibilidade.
- **PATCH**: correção compatível.

A versão do SDK é independente da versão da API REST (`/v1`), que segue o próprio ciclo. As mudanças de cada versão ficam no [CHANGELOG.md](CHANGELOG.md); as do produto, no [changelog público](https://docs.engineapi.com.br/changelog).

## Desenvolvimento

```bash
git clone https://github.com/3X-GIT/engineapi-sdk-python.git
cd engineapi-sdk-python
pip install -e ".[dev]"

pytest        # testes
ruff check .  # lint
```

## Suporte

- Documentação: [docs.engineapi.com.br](https://docs.engineapi.com.br)
- Dúvida ou defeito **neste SDK**: [abra uma issue](https://github.com/3X-GIT/engineapi-sdk-python/issues)
- Assuntos de conta, plano ou emissão: contato@3xtec.com.br
- Site: [engineapi.com.br](https://engineapi.com.br)

## Licença

MIT. Ver [LICENSE](LICENSE).
