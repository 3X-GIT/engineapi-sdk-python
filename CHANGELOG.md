# Changelog

Todas as mudanças relevantes deste SDK. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o versionamento é [SemVer](https://semver.org/lang/pt-BR/).

## 1.2.0

Primeira versão distribuída pelo PyPI. As versões anteriores circularam apenas junto do produto, sem publicação em registry.

### Adicionado

- ICMS monofásico de combustíveis (CST 02 e 61) para revenda de posto e GLP, com o modelo `CombustivelItem` e os campos `qBCMono`, `adRemICMS`, `vICMSMono`, `qBCMonoRet`, `adRemICMSRet` e `vICMSMonoRet` no item. Vale em NF-e e NFC-e, nos dois regimes.
- `cBenef` no item: código do benefício fiscal concedido pela UF, transcrito sem alteração para o documento. Algumas UFs exigem o campo quando o CST tem benefício.
- `desconto`, `valorFrete`, `valorSeguro`, `outrasDespesas` e `indTot` no item.
- Retenções na fonte da NFS-e (`RetencoesNfse`) e bloco `dpsNacional` do Padrão Nacional.

### Alterado

- `login()` desembrulha o envelope `{data, meta}` das respostas de sucesso, guarda o `access_token` e devolve o conteúdo de `data`. A chamada seguinte já sai autenticada.
- Cadastro de empresas emissoras em `/companies`, com o certificado digital A1 enviado em `multipart/form-data` (campos `file` e `password`).
- A mensagem de `EngineApiError` sai do corpo de erro no formato RFC 7807 (`error.detail`, com `error.title` como segunda opção).
- A superfície pública do SDK cobre NF-e, NFC-e e NFS-e.

### Corrigido

- Instalação do pacote pelo `pip`: a configuração de build passou a declarar o diretório `engineapi/` explicitamente.
