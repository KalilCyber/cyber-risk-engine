
from pathlib import Path

from fastapi import FastAPI, HTTPException

from servicos.inventario import Inventario
from infraestrutura.persistencia_json import Persistencia

from typing import Literal
from ipaddress import ip_address
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, field_validator, model_validator
from dominio.fabrica_ativos import FabricaAtivos


# Caminho absoluto para o JSON do projeto
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_DADOS = RAIZ_PROJETO / "ativos.json"

# Reutilizando as classes existentes
repositorio = Persistencia(str(CAMINHO_DADOS))
ativos_carregados = repositorio.carregar()

inventario = Inventario(
    ativos_carregados,
    repositorio
)

# Criação da aplicação HTTP
app = FastAPI(
    title="Cyber Risk Engine API",
    version="1.0.0"
)


@app.get("/health")
def verificar_saude():
    return {
        "status": "ok",
        "servico": "Cyber Risk Engine"
    }


@app.get("/ativos")
def listar_ativos():
    return [
        ativo.to_dict()
        for ativo in inventario.listar_ativos()
    ]


@app.get("/ativos/{id_ativo}")
def consultar_ativo(id_ativo: int):
    ativo = inventario.buscar_por_id(id_ativo)

    if ativo is None:
        raise HTTPException(
            status_code=404,
            detail="Ativo não encontrado."
        )

    return ativo.to_dict()


# Modelo dos dados recebidos pela API
class NovoAtivo(BaseModel):
    id: int = Field(gt=0)
    nome: str
    responsavel: str
    setor: str

    tipo: Literal[
        "Notebook", "Servidor", "Roteador", "AplicacaoWeb"
    ]

    processador: str | None = None
    servico: str | None = None
    endereco_ip: str | None = None
    url: str | None = None

    @field_validator(
        "nome", "responsavel", "setor",
        "processador", "servico"
    )
    @classmethod
    def validar_texto(cls, valor):
        if valor is None:
            return valor

        valor = valor.strip()

        if not any(letra.isalpha() for letra in valor):
            raise ValueError(
                "O campo deve conter texto válido."
            )

        return valor

    @model_validator(mode="after")
    def validar_atributo_especifico(self):
        campos = {
            "Notebook": "processador",
            "Servidor": "servico",
            "Roteador": "endereco_ip",
            "AplicacaoWeb": "url"
        }

        campo = campos[self.tipo]
        valor = getattr(self, campo)

        if not valor or not valor.strip():
            raise ValueError(
                f"O campo '{campo}' é obrigatório."
            )

        if self.tipo == "Roteador":
            try:
                ip_address(valor)
            except ValueError as erro:
                raise ValueError(
                    "Endereço IP inválido."
                ) from erro

        if self.tipo == "AplicacaoWeb":
            endereco = urlsplit(valor)

            if (
                endereco.scheme not in ("http", "https")
                or not endereco.hostname
            ):
                raise ValueError(
                    "A URL deve começar com http:// ou https:// "
                    "e conter um domínio válido."
                )

        return self


@app.post("/ativos", status_code=201)
def cadastrar_ativo_http(dados: NovoAtivo):

    # Verifica se o ID já existe
    if inventario.buscar_por_id(dados.id) is not None:
        raise HTTPException(
            status_code=409,
            detail="Já existe um ativo com este ID."
        )

    # Descobre o atributo específico da subclasse
    campos = {
        "Notebook": "processador",
        "Servidor": "servico",
        "Roteador": "endereco_ip",
        "AplicacaoWeb": "url"
    }

    campo = campos[dados.tipo]

    try:
        # Reutiliza a Factory existente
        ativo = FabricaAtivos.criar(
            dados.tipo,
            dados.id,
            dados.nome,
            dados.responsavel,
            dados.setor,
            [],
            **{campo: getattr(dados, campo)}
        )

        # Reutiliza as regras do Inventario
        inventario.cadastrar_ativo(ativo)

    except ValueError as erro:
        raise HTTPException(
            status_code=422,
            detail=str(erro)
        ) from erro

    try:
        inventario.salvar()

    except (OSError, ValueError, TypeError) as erro:
        # Desfaz o cadastro em memória se não salvar
        inventario.remover_ativo(ativo.id)

        raise HTTPException(
            status_code=500,
            detail="Falha ao persistir o ativo."
        ) from erro

    return ativo.to_dict()

