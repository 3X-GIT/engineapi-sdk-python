"""Engine API — Modelos Pydantic (type hints)."""

from __future__ import annotations

from typing import Any, Optional, Union

from pydantic import BaseModel


# ========================================
# Auth
# ========================================

class LoginParams(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    partner: dict[str, Any]


# ========================================
# Company / Issuer
# ========================================

class Endereco(BaseModel):
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    uf: str
    cep: str
    codigoMunicipio: Optional[str] = None


class CreateCompanyParams(BaseModel):
    cnpj: str
    razaoSocial: str
    nomeFantasia: Optional[str] = None
    inscricaoEstadual: Optional[str] = None
    inscricaoMunicipal: Optional[str] = None
    regime: str  # SIMPLES | LUCRO_PRESUMIDO | LUCRO_REAL
    endereco: Endereco


class Company(BaseModel):
    id: str
    cnpj: str
    razaoSocial: str
    nomeFantasia: Optional[str] = None
    inscricaoEstadual: Optional[str] = None
    regime: str
    createdAt: str


# ========================================
# NFe
# ========================================

class IcmsItem(BaseModel):
    origem: str
    # "02" e "61" sao a tributacao MONOFASICA de combustiveis (NT 2023.001):
    # valem nos dois regimes, inclusive Simples Nacional, e exigem o grupo
    # `combustivel` no mesmo item. Na NFC-e o leiaute so aceita o "61".
    cst: str
    aliquota: Optional[float] = None
    baseCalculo: Optional[float] = None
    # Monofasico CST 02 (tributacao propria). A base e uma QUANTIDADE (litro,
    # quilograma) e a aliquota e AD REM: reais por unidade, nao percentual.
    qBCMono: Optional[float] = None
    adRemICMS: Optional[float] = None
    vICMSMono: Optional[float] = None
    # Monofasico CST 61 (cobrado anteriormente: revenda de posto/GLP).
    qBCMonoRet: Optional[float] = None
    adRemICMSRet: Optional[float] = None
    vICMSMonoRet: Optional[float] = None


class CombustivelItem(BaseModel):
    """Grupo comb/LA — obrigatorio junto com a tributacao monofasica."""

    cProdANP: str
    descANP: str
    ufConsumo: str
    pGLP: Optional[float] = None
    pGNn: Optional[float] = None
    pGNi: Optional[float] = None
    vPart: Optional[float] = None


class NfeItem(BaseModel):
    descricao: str
    ncm: str
    cfop: str
    unidade: str
    quantidade: float
    valorUnitario: float
    valorTotal: float
    desconto: Optional[float] = None
    # cBenef: codigo do beneficio fiscal concedido pela UF, 8 ou 10 caracteres
    # alfanumericos (ex.: "GO810003") ou o literal "SEM CBENEF". O codigo vem
    # da tabela de beneficios da propria UF e e transcrito para o documento sem
    # alteracao. Algumas UFs exigem o campo quando o CST tem beneficio (ex.: GO
    # rejeita com cStat 930 o CST 61 monofasico de combustivel sem cBenef).
    # Reusado tambem pela NFC-e (CreateNfceParams.itens usa este mesmo modelo).
    cBenef: Optional[str] = None
    # Frete/seguro/outras despesas do item (vFrete/vSeg/vOutro do leiaute):
    # somam no vNF e aumentam a base do ICMS/IBS-CBS — o inverso do desconto.
    valorFrete: Optional[float] = None
    valorSeguro: Optional[float] = None
    outrasDespesas: Optional[float] = None
    # indTot do leiaute: 1 (default) compõe o vProd/vNF do total; 0 não compõe.
    indTot: Optional[int] = None
    icms: Optional[IcmsItem] = None
    combustivel: Optional[CombustivelItem] = None


class Destinatario(BaseModel):
    cnpjCpf: str
    razaoSocial: str
    inscricaoEstadual: Optional[str] = None
    endereco: Endereco


class Emitente(BaseModel):
    issuerId: str


class CreateNfeParams(BaseModel):
    emitente: Emitente
    destinatario: Destinatario
    itens: list[NfeItem]
    naturezaOperacao: Optional[str] = None
    informacoesAdicionais: Optional[str] = None


class NfeResponse(BaseModel):
    id: str
    accessKey: Optional[str] = None
    status: str
    protocolo: Optional[str] = None
    numero: Optional[int] = None
    serie: Optional[int] = None
    xml: Optional[str] = None
    createdAt: str


class CancelNfeParams(BaseModel):
    justificativa: str


class CartaCorrecaoParams(BaseModel):
    correcao: str


# ========================================
# NFCe
# ========================================

class PagamentoNfce(BaseModel):
    tipo: str
    valor: float


class CreateNfceParams(BaseModel):
    issuerId: str
    itens: list[NfeItem]
    pagamento: PagamentoNfce
    cpfConsumidor: Optional[str] = None


# ========================================
# MDFe
# Modelos de contrato apenas. Este SDK não expõe cliente de MDFe: a
# superfície pública cobre NFe, NFCe e NFSe.
# ========================================

class VeiculoMdfe(BaseModel):
    placa: str
    renavam: Optional[str] = None
    tara: int
    capacidadeKg: int


class MotoristaMdfe(BaseModel):
    nome: str
    cpf: str


class DocumentosMdfe(BaseModel):
    chaveNfe: Optional[list[str]] = None
    chaveCte: Optional[list[str]] = None


class CreateMdfeParams(BaseModel):
    issuerId: str
    ufCarregamento: str
    ufDescarregamento: str
    modalidade: str  # RODOVIARIO | AEREO | AQUAVIARIO | FERROVIARIO
    veiculo: VeiculoMdfe
    motorista: MotoristaMdfe
    documentos: DocumentosMdfe
    valorCarga: float
    pesoBruto: float


# ========================================
# NFSe
# ========================================

class TomadorNfse(BaseModel):
    cnpjCpf: str
    razaoSocial: str
    endereco: Optional[Endereco] = None


class ServicoNfse(BaseModel):
    # Nomes do contrato real (`POST /v1/nfse`): `discriminacao`,
    # `itemListaServico` e `codigoMunicipio`. O contrato de emissão é ESTRITO
    # desde a v2 — campo com outro nome recusa com 400 apontando o certo.
    codigoMunicipio: str
    itemListaServico: Optional[str] = None
    discriminacao: str
    valorServicos: float
    aliquotaIss: Optional[float] = None
    valorDeducoes: Optional[float] = None
    descontoIncondicionado: Optional[float] = None
    descontoCondicionado: Optional[float] = None


class RetencoesNfse(BaseModel):
    """Retenções na fonte, com efeito real no documento.

    Informe o valor RETIDO em reais; a engineAPI escolhe o campo do leiaute
    da DPS e confere coerência, sem calcular alíquota nenhuma.

    - issRetidoPor: "tomador" (tpRetISSQN=2) ou "intermediario" (3). O leiaute
      não tem campo para o VALOR do ISS retido — o sistema nacional o calcula
      a partir deste indicador.
    - irrf/csll/inss: vão para vRetIRRF / vRetCSLL / vRetCP.
    - pis/cofins/outrasRetencoes: SEM campo de valor no leiaute (vPis/vCofins
      da DPS são debito de apuracao propria, nao retencao, e ficam fora do
      total de retencoes). Valor != 0 recusa com 422
      RETENCAO_SEM_CAMPO_NO_LEIAUTE: declare a retencao de PIS/COFINS pelo
      indicador `dpsNacional.tpRetPisCofins`.
    """

    issRetidoPor: Optional[str] = None  # "tomador" | "intermediario"
    irrf: Optional[float] = None
    csll: Optional[float] = None
    cofins: Optional[float] = None
    pis: Optional[float] = None
    inss: Optional[float] = None
    outrasRetencoes: Optional[float] = None


class DpsNacionalNfse(BaseModel):
    """Bloco do Padrão Nacional (passthrough — a engineAPI só transcreve)."""

    opSimpNac: Union[str, int]  # 1=Não Optante, 2=MEI, 3=ME/EPP
    cTribNac: str
    tribISSQN: Union[str, int]
    regApTribSN: Optional[Union[str, int]] = None
    regEspTrib: Optional[Union[str, int]] = None
    cTribMun: Optional[str] = None
    # 1=não retido, 2=retido pelo tomador, 3=retido pelo intermediário.
    tpRetISSQN: Optional[Union[str, int]] = None
    cstPisCofins: Optional[str] = None
    # 0 a 9: e por aqui que a retencao de PIS/COFINS se declara (o leiaute
    # nao tem campo para o valor retido deles). Passthrough puro; exige
    # cstPisCofins.
    tpRetPisCofins: Optional[Union[str, int]] = None
    pTotTribSN: Optional[float] = None


class CreateNfseParams(BaseModel):
    issuerId: str
    tomador: TomadorNfse
    servico: ServicoNfse
    dpsNacional: Optional[DpsNacionalNfse] = None
    retencoes: Optional[RetencoesNfse] = None
    competencia: Optional[str] = None
    resolverTributacao: Optional[bool] = None


# ========================================
# Pagination
# ========================================

class PaginationParams(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    sortBy: Optional[str] = None
    sortOrder: Optional[str] = None  # asc | desc
