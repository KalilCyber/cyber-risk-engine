import json
import importlib

import pytest
from fastapi.testclient import TestClient

from servicos.inventario import Inventario
from infraestrutura.persistencia_json import Persistencia


# Importamos o módulo da API
modulo_api = importlib.import_module("api.app")


@pytest.fixture
def ambiente_teste(tmp_path, monkeypatch):
    """
    Cria um inventário isolado para cada teste.

    O arquivo ativos.json original não será alterado.
    """

    arquivo_temporario = tmp_path / "ativos_teste.json"

    repositorio = Persistencia(
        str(arquivo_temporario)
    )

    inventario_teste = Inventario(
        [],
        repositorio=repositorio
    )

    # A API passa a utilizar o inventário temporário
    monkeypatch.setattr(
        modulo_api,
        "inventario",
        inventario_teste
    )

    with TestClient(modulo_api.app) as cliente:
        yield cliente, repositorio


@pytest.fixture
def dados_notebook():
    """
    Dados válidos para cadastrar um notebook.
    """

    return {
        "id": 9001,
        "nome": "Notebook Teste Pytest",
        "responsavel": "Aline",
        "setor": "Cibersegurança",
        "tipo": "Notebook",
        "processador": "Intel Core i5"
    }


def test_health(ambiente_teste):
    cliente, _ = ambiente_teste

    resposta = cliente.get("/health")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


def test_listagem_inicial_vazia(ambiente_teste):
    cliente, _ = ambiente_teste

    resposta = cliente.get("/ativos")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_consultar_ativo_inexistente(ambiente_teste):
    cliente, _ = ambiente_teste

    resposta = cliente.get("/ativos/999999")

    assert resposta.status_code == 404


def test_cadastrar_ativo(
    ambiente_teste,
    dados_notebook
):
    cliente, _ = ambiente_teste

    resposta = cliente.post(
        "/ativos",
        json=dados_notebook
    )

    assert resposta.status_code == 201
    assert resposta.json()["id"] == 9001
    assert resposta.json()["nome"] == "Notebook Teste Pytest"


def test_consultar_ativo_cadastrado(
    ambiente_teste,
    dados_notebook
):
    cliente, _ = ambiente_teste

    cliente.post("/ativos", json=dados_notebook)

    resposta = cliente.get("/ativos/9001")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == 9001


def test_rejeitar_id_duplicado(
    ambiente_teste,
    dados_notebook
):
    cliente, _ = ambiente_teste

    cliente.post("/ativos", json=dados_notebook)

    resposta = cliente.post(
        "/ativos",
        json=dados_notebook
    )

    assert resposta.status_code == 409


def test_rejeitar_processador_invalido(
    ambiente_teste,
    dados_notebook
):
    cliente, _ = ambiente_teste

    dados_notebook["processador"] = "-2"

    resposta = cliente.post(
        "/ativos",
        json=dados_notebook
    )

    assert resposta.status_code == 422


def test_persistencia_json(
    ambiente_teste,
    dados_notebook
):
    cliente, repositorio = ambiente_teste

    resposta = cliente.post(
        "/ativos",
        json=dados_notebook
    )

    assert resposta.status_code == 201

    # Recupera diretamente do JSON temporário
    ativos_recuperados = repositorio.carregar()

    assert len(ativos_recuperados) == 1
    assert ativos_recuperados[0].id == 9001
    assert ativos_recuperados[0].nome == "Notebook Teste Pytest"



# =========================================================
# TESTES DE REGRESSÃO DA PERSISTÊNCIA
# =========================================================

def test_reconstruir_ativo_sem_vulnerabilidades(
    ambiente_teste,
    dados_notebook
):
    cliente, repositorio = ambiente_teste

    resposta = cliente.post(
        "/ativos",
        json=dados_notebook
    )

    assert resposta.status_code == 201

    ativos = repositorio.carregar()

    assert len(ativos) == 1
    assert ativos[0].vulnerabilidades == []


def test_dependencia_com_ativo_posterior_no_json(
    ambiente_teste,
    dados_notebook
):
    cliente, repositorio = ambiente_teste

    # Primeiro cadastramos o ativo ID 7
    primeiro = dados_notebook.copy()
    primeiro["id"] = 7

    # Depois cadastramos o ativo ID 23
    segundo = dados_notebook.copy()
    segundo["id"] = 23
    segundo["nome"] = "Notebook Dependencia"

    assert cliente.post(
        "/ativos", json=primeiro
    ).status_code == 201

    assert cliente.post(
        "/ativos", json=segundo
    ).status_code == 201

    # Alteramos somente o JSON temporário do pytest
    with open(
        repositorio.arquivo_dados,
        "r",
        encoding="utf-8"
    ) as arquivo:
        dados = json.load(arquivo)

    dados[0]["dependencias"] = [
        {
            "id_ativo_origem": 23,
            "peso": 0.25
        }
    ]

    with open(
        repositorio.arquivo_dados,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False)

    # Deve reconhecer o ID 23 mesmo aparecendo depois
    ativos = repositorio.carregar()

    assert len(ativos) == 2
    assert ativos[0].id == 7
    assert ativos[1].id == 23
    assert (
        ativos[0].dependencias[0]["id_ativo_origem"]
        == 23
    )


def test_rejeitar_dependencia_inexistente(
    ambiente_teste,
    dados_notebook
):
    cliente, repositorio = ambiente_teste

    assert cliente.post(
        "/ativos",
        json=dados_notebook
    ).status_code == 201

    with open(
        repositorio.arquivo_dados,
        "r",
        encoding="utf-8"
    ) as arquivo:
        dados = json.load(arquivo)

    dados[0]["dependencias"] = [
        {
            "id_ativo_origem": 99999,
            "peso": 0.25
        }
    ]

    with open(
        repositorio.arquivo_dados,
        "w",
        encoding="utf-8"
    ) as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False)

    with pytest.raises(
        ValueError,
        match="dependência aponta"
    ):
        repositorio.carregar()
