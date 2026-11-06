"""Testes adicionais para a API usada pelo frontend.

Dependem das duas linhas de integração em api/app.py, explicadas no README.
Não usam o ativos.json real.
"""
import importlib

import pytest
from fastapi.testclient import TestClient

from infraestrutura.persistencia_json import Persistencia
from servicos.inventario import Inventario
from servicos.servico_cve import ServicoCVE

appmod = importlib.import_module("api.app")


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    repo = Persistencia(str(tmp_path / "ativos_web.json"))
    inv = Inventario([], repositorio=repo)
    monkeypatch.setattr(appmod, "inventario", inv)
    with TestClient(appmod.app) as test_client:
        yield test_client, repo


def cadastrar(client, id_ativo, nome):
    response = client.post("/ativos", json={
        "id": id_ativo, "nome": nome, "tipo": "Notebook",
        "responsavel": "Aline", "setor": "Cibersegurança",
        "processador": "Intel Core i5"
    })
    assert response.status_code == 201, response.text


def test_editar_remover_ativo_e_persistencia(cliente):
    client, repo = cliente
    cadastrar(client, 101, "Notebook Vigília")
    r = client.put("/ativos/101", json={"nome": "Notebook Atualizado"})
    assert r.status_code == 200, r.text
    assert r.json()["nome"] == "Notebook Atualizado"
    assert repo.carregar()[0].nome == "Notebook Atualizado"
    r = client.delete("/ativos/101")
    assert r.status_code == 200, r.text
    assert client.get("/ativos/101").status_code == 404
    assert repo.carregar() == []


def test_cadastro_edicao_remocao_vulnerabilidade(cliente):
    client, repo = cliente
    cadastrar(client, 101, "Notebook Vigília")
    dados = {"id": 501, "descricao": "Falha XSS", "categoria": "CWE-79", "severidade": 6.4, "status": "ABERTO"}
    resposta = client.post("/ativos/101/vulnerabilidades", json=dados)
    assert resposta.status_code == 201, resposta.text
    r = client.patch("/ativos/101/vulnerabilidades/501", json={"status": "CORRIGIDA"})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "CORRIGIDA"
    assert repo.carregar()[0].vulnerabilidades[0].status.name == "CORRIGIDA"
    r = client.delete("/ativos/101/vulnerabilidades/501")
    assert r.status_code == 200, r.text
    assert client.get("/ativos/101/vulnerabilidades").json() == []


def test_dependencias_e_risco(cliente):
    client, _ = cliente
    cadastrar(client, 101, "Notebook A")
    cadastrar(client, 102, "Notebook B")
    v = {"id": 501, "descricao": "Falha XSS", "categoria": "CWE-79", "severidade": 6.4, "status": "ABERTO"}
    assert client.post("/ativos/102/vulnerabilidades", json=v).status_code == 201
    r = client.post("/ativos/101/dependencias", json={"origem_id": 102, "nivel": "MODERADA"})
    assert r.status_code == 201, r.text
    deps = client.get("/ativos/101/dependencias").json()
    assert deps[0]["peso"] == pytest.approx(0.25)
    risco = client.get("/risco")
    assert risco.status_code == 200, risco.text
    riscos = {a["id"]: a for a in risco.json()["ativos"]}
    assert riscos[102]["risco_efetivo"] == pytest.approx(6.4)
    assert riscos[101]["risco_efetivo"] == pytest.approx(1.6)
    assert client.delete("/ativos/101/dependencias/102").status_code == 200
    assert client.get("/ativos/101/dependencias").json() == []


def test_validacao_nao_modifica_dados(cliente):
    client, repo = cliente
    cadastrar(client, 101, "Notebook Vigília")
    r = client.post("/ativos/101/vulnerabilidades", json={
        "id": 501, "descricao": "XSS", "categoria": "CWE-79", "severidade": 12.0
    })
    assert r.status_code == 422
    assert repo.carregar()[0].vulnerabilidades == []
    assert client.put("/ativos/101", json={"responsavel": "-2"}).status_code == 422
    assert repo.carregar()[0].responsavel == "Aline"


def test_consulta_nvd_com_dados_simulados(cliente, monkeypatch):
    client, _ = cliente
    monkeypatch.setattr(ServicoCVE, "pesquisar_por_nome", lambda self, termo, limite=8: [{
        "cve_id": "CVE-2026-12345", "descricao": "Exemplo de teste",
        "cwe_id": "CWE-79", "cvss": {"score": 7.1, "versao": "3.1", "vetor": "CVSS:3.1/..."}
    }])
    r = client.get("/cves?termo=XSS")
    assert r.status_code == 200, r.text
    assert r.json()[0]["cve_id"] == "CVE-2026-12345"
