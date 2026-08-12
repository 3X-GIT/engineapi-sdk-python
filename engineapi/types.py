"""Modelos Pydantic do contrato público da Engine API.

Os nomes dos campos reproduzem literalmente o OpenAPI publicado.  Os modelos
rejeitam campos desconhecidos, como os DTOs Zod da API.
"""

from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, ConfigDict


class EngineApiModel(BaseModel):
    """Base para os objetos estritos aceitos pelos DTOs de emissão."""

    model_config = ConfigDict(extra="forbid")


# ========================================
# Auth
# ========================================


class LoginParams(EngineApiModel):
    email: str
    password: str


class LoginResponse(EngineApiModel):
    access_token: str
    partnerId: str


# ========================================
# Companies / issuers
# ========================================


class CreateCompanyParams(EngineApiModel):
    """Corpo de ``POST /v1/companies`` (endereço em campos planos)."""

    cnpj: str
    name: str
    tradeName: Optional[str] = None
    ie: Optional[str] = None
    im: Optional[str] = None
    crt: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cep: Optional[str] = None
    address: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    ibgeCode: Optional[str] = None
    csc: Optional[str] = None
    cscId: Optional[str] = None
    cnae: Optional[str] = None
    segmento: Optional[str] = None
    mei: Optional[bool] = None
    fiscalBrainEnabled: Optional[bool] = None
    cTribNacPadrao: Optional[str] = None
    servicoPadraoLc116: Optional[str] = None
    pTotTribSNPadrao: Optional[float] = None


class Company(EngineApiModel):
    """Resposta de empresa sem os segredos ``csc`` e ``certPassword``."""

    id: str
    cnpj: str
    name: str
    crt: int
    certExpiryUnknown: bool
    sandbox: bool
    ambienteFiscal: int
    fiscalBrainEnabled: bool
    mei: bool
    createdAt: str
    updatedAt: str
    tradeName: Optional[str] = None
    ie: Optional[str] = None
    im: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    cep: Optional[str] = None
    address: Optional[str] = None
    number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    ibgeCode: Optional[str] = None
    certFilename: Optional[str] = None
    certExpiry: Optional[str] = None
    cscId: Optional[str] = None
    cnae: Optional[str] = None
    segmento: Optional[str] = None
    servicoPadraoLc116: Optional[str] = None
    issMunicipio: Optional[str] = None
    cTribNacPadrao: Optional[str] = None
    pTotTribSNPadrao: Optional[float] = None
    partnerId: Optional[str] = None


# ========================================
# Shared NFe / NFCe shapes
# ========================================


class Endereco(EngineApiModel):
    """Endereço do destinatário da NF-e."""

    logradouro: str
    numero: str
    bairro: str
    codigoMunicipio: str
    municipio: str
    uf: str
    cep: str
    complemento: Optional[str] = None


class Destinatario(EngineApiModel):
    cnpjCpf: str
    nome: str
    endereco: Endereco
    ie: Optional[str] = None
    indicadorIE: Optional[int] = None
    email: Optional[str] = None


class IcmsItem(EngineApiModel):
    origem: Optional[int] = None
    cst: Optional[str] = None
    csosn: Optional[str] = None
    aliquota: Optional[float] = None
    baseCalculo: Optional[float] = None
    valor: Optional[float] = None
    baseCalculoST: Optional[float] = None
    aliquotaST: Optional[float] = None
    valorST: Optional[float] = None
    modBC: Optional[str] = None
    pRedBC: Optional[float] = None
    vBC: Optional[float] = None
    pICMS: Optional[float] = None
    vICMS: Optional[float] = None
    vBCFCP: Optional[float] = None
    pFCP: Optional[float] = None
    vFCP: Optional[float] = None
    modBCST: Optional[str] = None
    pMVAST: Optional[float] = None
    pRedBCST: Optional[float] = None
    vBCST: Optional[float] = None
    pICMSST: Optional[float] = None
    vICMSST: Optional[float] = None
    vBCFCPST: Optional[float] = None
    pFCPST: Optional[float] = None
    vFCPST: Optional[float] = None
    vBCSTRet: Optional[float] = None
    pST: Optional[float] = None
    vICMSSubstituto: Optional[float] = None
    vICMSSTRet: Optional[float] = None
    vBCFCPSTRet: Optional[float] = None
    pFCPSTRet: Optional[float] = None
    vFCPSTRet: Optional[float] = None
    pRedBCEfet: Optional[float] = None
    vBCEfet: Optional[float] = None
    pICMSEfet: Optional[float] = None
    vICMSEfet: Optional[float] = None
    qBCMono: Optional[float] = None
    adRemICMS: Optional[float] = None
    vICMSMono: Optional[float] = None
    qBCMonoRet: Optional[float] = None
    adRemICMSRet: Optional[float] = None
    vICMSMonoRet: Optional[float] = None


class IcmsNfceItem(EngineApiModel):
    origem: Optional[int] = None
    csosn: Optional[str] = None
    cst: Optional[str] = None
    aliquota: Optional[float] = None
    baseCalculo: Optional[float] = None
    valor: Optional[float] = None
    baseCalculoST: Optional[float] = None
    aliquotaST: Optional[float] = None
    valorST: Optional[float] = None
    qBCMono: Optional[float] = None
    adRemICMS: Optional[float] = None
    vICMSMono: Optional[float] = None
    qBCMonoRet: Optional[float] = None
    adRemICMSRet: Optional[float] = None
    vICMSMonoRet: Optional[float] = None


class PisItem(EngineApiModel):
    cst: Optional[str] = None
    baseCalculo: Optional[float] = None
    aliquota: Optional[float] = None
    valor: Optional[float] = None


class CofinsItem(PisItem):
    pass


class IpiItem(PisItem):
    cEnq: Optional[str] = None


class IbsCbsComponente(EngineApiModel):
    p: float
    pNominal: Optional[float] = None
    pRedAliq: Optional[float] = None
    v: Optional[float] = None


class IbsCbsItem(EngineApiModel):
    cst: Optional[str] = None
    cClassTrib: Optional[str] = None
    vBC: Optional[float] = None
    ibsUf: IbsCbsComponente
    ibsMun: IbsCbsComponente
    vIbs: Optional[float] = None
    cbs: IbsCbsComponente


class IbsCbsClasse(EngineApiModel):
    cClassTrib: str


class CombustivelItem(EngineApiModel):
    cProdANP: str
    descANP: str
    ufConsumo: str
    pGLP: Optional[float] = None
    pGNn: Optional[float] = None
    pGNi: Optional[float] = None
    vPart: Optional[float] = None


class NfeItem(EngineApiModel):
    codigo: str
    descricao: str
    ncm: str
    cfop: str
    unidade: str
    quantidade: float
    valorUnitario: float
    ean: Optional[str] = None
    cest: Optional[str] = None
    cBenef: Optional[str] = None
    valorTotal: Optional[float] = None
    desconto: Optional[float] = None
    valorFrete: Optional[float] = None
    valorSeguro: Optional[float] = None
    outrasDespesas: Optional[float] = None
    indTot: Optional[Literal[0, 1]] = None
    icms: Optional[IcmsItem] = None
    pis: Optional[PisItem] = None
    cofins: Optional[CofinsItem] = None
    ipi: Optional[IpiItem] = None
    ibsCbs: Optional[Union[IbsCbsItem, IbsCbsClasse]] = None
    combustivel: Optional[CombustivelItem] = None


class NfceItem(EngineApiModel):
    codigo: str
    descricao: str
    ncm: str
    cfop: str
    unidade: str
    quantidade: float
    valorUnitario: float
    ean: Optional[str] = None
    cest: Optional[str] = None
    cBenef: Optional[str] = None
    valorTotal: Optional[float] = None
    desconto: Optional[float] = None
    valorFrete: Optional[float] = None
    valorSeguro: Optional[float] = None
    outrasDespesas: Optional[float] = None
    indTot: Optional[Literal[1]] = None
    icms: Optional[IcmsNfceItem] = None
    pis: Optional[PisItem] = None
    cofins: Optional[CofinsItem] = None
    ipi: Optional[IpiItem] = None
    ibsCbs: Optional[Union[IbsCbsItem, IbsCbsClasse]] = None
    combustivel: Optional[CombustivelItem] = None


class Pagamento(EngineApiModel):
    forma: str
    valor: float


class Fatura(EngineApiModel):
    numero: str
    valorOriginal: float
    valorDesconto: float
    valorLiquido: float


class Duplicata(EngineApiModel):
    vencimento: str
    valor: float
    numero: Optional[str] = None


class Cobranca(EngineApiModel):
    fatura: Optional[Fatura] = None
    duplicatas: Optional[list[Duplicata]] = None


# ========================================
# NFe (modelo 55)
# ========================================


class Referenciada(EngineApiModel):
    chaveAcesso: str


class Transportadora(EngineApiModel):
    cnpjCpf: Optional[str] = None
    nome: Optional[str] = None
    ie: Optional[str] = None
    endereco: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None


class Volume(EngineApiModel):
    quantidade: Optional[int] = None
    especie: Optional[str] = None
    pesoBruto: Optional[float] = None
    pesoLiquido: Optional[float] = None


class Transporte(EngineApiModel):
    modFrete: Literal[0, 1, 2, 3, 4, 9]
    transportadora: Optional[Transportadora] = None
    volumes: Optional[list[Volume]] = None


class CreateNfeParams(EngineApiModel):
    destinatario: Destinatario
    items: list[NfeItem]
    pagamentos: list[Pagamento]
    issuerId: Optional[str] = None
    naturezaOperacao: Optional[str] = None
    serie: Optional[int] = None
    numero: Optional[int] = None
    tpNF: Optional[int] = None
    idDest: Optional[int] = None
    indFinal: Optional[int] = None
    indPres: Optional[int] = None
    finNFe: Optional[int] = None
    referenciadas: Optional[list[Referenciada]] = None
    transporte: Optional[Transporte] = None
    troco: Optional[float] = None
    cobranca: Optional[Cobranca] = None
    informacoesComplementares: Optional[str] = None
    informacoesFisco: Optional[str] = None
    resolverTributacao: Optional[bool] = None


class NfeDownloads(EngineApiModel):
    xml: str
    pdf: str


class NfeResponse(EngineApiModel):
    """Resposta de emissão de ``POST /v1/nfe`` e da fila."""

    id: str
    status: str
    number: int
    series: int
    model: str
    amount: str
    createdAt: str
    updatedAt: str
    accessKey: Optional[str] = None
    protocol: Optional[str] = None
    destCNPJ: Optional[str] = None
    destName: Optional[str] = None
    downloads: Optional[NfeDownloads] = None


class CancelNfeParams(EngineApiModel):
    justificativa: str


class CartaCorrecaoParams(EngineApiModel):
    correcao: str


# ========================================
# NFCe (modelo 65)
# ========================================


class CreateNfceParams(EngineApiModel):
    items: list[NfceItem]
    pagamentos: list[Pagamento]
    issuerId: Optional[str] = None
    serie: Optional[float] = None
    numero: Optional[float] = None
    destCPF: Optional[str] = None
    destNome: Optional[str] = None
    indPres: Optional[Literal[1, 2, 3, 4, 5, 9]] = None
    troco: Optional[float] = None
    cobranca: Optional[Cobranca] = None
    informacoesComplementares: Optional[str] = None
    resolverTributacao: Optional[bool] = None


# ========================================
# NFSe
# ========================================


class EnderecoNfse(EngineApiModel):
    logradouro: str
    numero: str
    bairro: str
    codigoMunicipio: str
    uf: str
    cep: str
    complemento: Optional[str] = None


class TomadorNfse(EngineApiModel):
    cnpjCpf: str
    razaoSocial: str
    endereco: EnderecoNfse
    email: Optional[str] = None
    telefone: Optional[str] = None
    inscricaoMunicipal: Optional[str] = None


class ServicoNfse(EngineApiModel):
    codigoMunicipio: str
    discriminacao: str
    valorServicos: float
    itemListaServico: Optional[str] = None
    codigoCnae: Optional[str] = None
    codigoTributacaoMunicipio: Optional[str] = None
    codigoNBS: Optional[str] = None
    aliquotaIss: Optional[float] = None
    valorDeducoes: Optional[float] = None
    descontoIncondicionado: Optional[float] = None
    descontoCondicionado: Optional[float] = None


class RpsNfse(EngineApiModel):
    numero: int
    serie: Optional[str] = None
    tipo: Optional[int] = None


class RetencoesNfse(EngineApiModel):
    issRetidoPor: Optional[Literal["tomador", "intermediario"]] = None
    irrf: Optional[float] = None
    csll: Optional[float] = None
    inss: Optional[float] = None
    cofins: Optional[float] = None
    pis: Optional[float] = None
    outrasRetencoes: Optional[float] = None


class DpsNacionalNfse(EngineApiModel):
    opSimpNac: Union[str, int]
    cTribNac: str
    tribISSQN: Union[str, int]
    regApTribSN: Optional[Union[str, int]] = None
    regEspTrib: Optional[Union[str, int]] = None
    cTribMun: Optional[str] = None
    tpRetISSQN: Optional[Union[str, int]] = None
    cstPisCofins: Optional[str] = None
    tpRetPisCofins: Optional[Union[str, int]] = None
    pTotTribSN: Optional[float] = None


class IbsCbsDiferimentoNfse(EngineApiModel):
    pDifUF: float
    pDifMun: float
    pDifCBS: float


class IbsCbsTributacaoRegularNfse(EngineApiModel):
    cstReg: str
    cClassTribReg: str


class IbsCbsNfse(EngineApiModel):
    cIndOp: str
    cst: str
    cClassTrib: str
    finNFSe: Optional[Literal["0"]] = None
    indFinal: Optional[Literal["0", "1"]] = None
    tpOper: Optional[Literal["1", "2", "3", "4", "5"]] = None
    tpEnteGov: Optional[Literal["1", "2", "3", "4"]] = None
    indDest: Optional[Literal["0", "1"]] = None
    cCredPres: Optional[str] = None
    gTribRegular: Optional[IbsCbsTributacaoRegularNfse] = None
    gDif: Optional[IbsCbsDiferimentoNfse] = None


class CreateNfseParams(EngineApiModel):
    issuerId: str
    tomador: TomadorNfse
    servico: ServicoNfse
    rps: Optional[RpsNfse] = None
    serie: Optional[Union[str, int]] = None
    dpsNacional: Optional[DpsNacionalNfse] = None
    ibsCbs: Optional[IbsCbsNfse] = None
    naturezaOperacao: Optional[int] = None
    regimeTributacao: Optional[int] = None
    optanteSimples: Optional[bool] = None
    exigibilidadeISS: Optional[int] = None
    competencia: Optional[str] = None
    retencoes: Optional[RetencoesNfse] = None
    informacoesComplementares: Optional[str] = None
    resolverTributacao: Optional[bool] = None


# ========================================
# Query parameters
# ========================================


class PaginationParams(EngineApiModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    sortBy: Optional[str] = None
    sortOrder: Optional[Literal["asc", "desc"]] = None
