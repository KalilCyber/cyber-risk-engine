"""Testes independentes do diário — não tocam ativos.json."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.diario_cacada import instalar_diario, caminho_diario


class VulnerabilidadeFake:
    def __init__(self):
        self.id = 501
        self.cve_id = "CVE-TESTE"
        self.status = "ABERTO"


class AtivoFake:
    def __init__(self):
        self.id = 9001
        self.nome = "Notebook do Caçador"
        self.vulnerabilidades = [VulnerabilidadeFake()]
        self.dependencias = []


class InventarioFake:
    def __init__(self):
        self.ativos = [AtivoFake()]

    def listar_ativos(self):
        return self.ativos


def test_diario_registra_transicao_e_persiste(tmp_path, monkeypatch):
    path = tmp_path / "eventos.jsonl"
    monkeypatch.setenv("CYBER_RISK_JOURNAL", str(path))
    assert caminho_diario() == path
    inventario = InventarioFake()
    app = FastAPI()

    @app.patch("/ativos/9001/vulnerabilidades/501")
    def corrigir():
        inventario.ativos[0].vulnerabilidades[0].status = "CORRIGIDA"
        return {"status": "CORRIGIDA"}

    instalar_diario(app, lambda: inventario)
    with TestClient(app) as client:
        assert client.get("/diario").json()["total"] == 0
        assert client.patch("/ativos/9001/vulnerabilidades/501").status_code == 200
        registros = client.get("/diario").json()
        assert registros["total"] == 1
        assert registros["resumo"]["corrigidas"] == 1
        assert registros["eventos"][0]["status_anterior"] == "ABERTO"
        assert registros["eventos"][0]["status_novo"] == "CORRIGIDA"
        assert path.is_file()
        assert client.patch("/ativos/9001/vulnerabilidades/501").status_code == 200
        assert client.get("/diario").json()["total"] == 1


def test_requisicao_com_erro_nao_gera_evento(tmp_path, monkeypatch):
    monkeypatch.setenv("CYBER_RISK_JOURNAL", str(tmp_path / "diario.jsonl"))
    inventario = InventarioFake()
    app = FastAPI()

    @app.patch("/ativos/9001/vulnerabilidades/501")
    def rejeitar():
        from fastapi import HTTPException
        raise HTTPException(422, "Operação inválida")

    instalar_diario(app, lambda: inventario)
    with TestClient(app) as client:
        assert client.patch("/ativos/9001/vulnerabilidades/501").status_code == 422
        assert client.get("/diario").json()["total"] == 0
