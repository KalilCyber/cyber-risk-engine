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


def test_diario_detecta_atributo_do_ativo_sem_mudar_nome(tmp_path, monkeypatch):
    monkeypatch.setenv("CYBER_RISK_JOURNAL", str(tmp_path / "eventos.jsonl"))
    inventario = InventarioFake()
    inventario.ativos[0].processador = "Intel Core i5"
    app = FastAPI()

    @app.put("/ativos/9001")
    def atualizar():
        inventario.ativos[0].processador = "AMD Ryzen 7"
        return {"ok": True}

    instalar_diario(app, lambda: inventario)
    with TestClient(app) as client:
        assert client.put("/ativos/9001").status_code == 200
        diario = client.get("/diario").json()
        assert diario["total"] == 1
        evento = diario["eventos"][0]
        assert evento["tipo"] == "ativo_atualizado"
        assert evento["alteracoes"]["processador"] == {
            "anterior": "Intel Core i5", "novo": "AMD Ryzen 7"
        }
        # Repetir uma operação sem mudança real não cria eventos.
        assert client.put("/ativos/9001").status_code == 200
        assert client.get("/diario").json()["total"] == 1


def test_diario_detecta_cvss_sem_mudar_status(tmp_path, monkeypatch):
    monkeypatch.setenv("CYBER_RISK_JOURNAL", str(tmp_path / "eventos.jsonl"))
    inventario = InventarioFake()
    inventario.ativos[0].vulnerabilidades[0].severidade = 6.4
    inventario.ativos[0].vulnerabilidades[0].descricao = "Falha XSS"
    app = FastAPI()

    @app.patch("/ativos/9001/vulnerabilidades/501")
    def atualizar():
        vulnerabilidade = inventario.ativos[0].vulnerabilidades[0]
        vulnerabilidade.severidade = 8.1
        vulnerabilidade.descricao = "Falha XSS corrigir"
        return {"ok": True}

    instalar_diario(app, lambda: inventario)
    with TestClient(app) as client:
        assert client.patch("/ativos/9001/vulnerabilidades/501").status_code == 200
        diario = client.get("/diario").json()
        assert diario["total"] == 1
        evento = diario["eventos"][0]
        assert evento["tipo"] == "vulnerabilidade_atualizada"
        assert evento["alteracoes"]["severidade"] == {"anterior": 6.4, "novo": 8.1}
        assert evento["alteracoes"]["descricao"]["novo"] == "Falha XSS corrigir"


def test_diario_detecta_peso_de_dependencia(tmp_path, monkeypatch):
    monkeypatch.setenv("CYBER_RISK_JOURNAL", str(tmp_path / "eventos.jsonl"))
    inventario = InventarioFake()
    inventario.ativos[0].dependencias = [{"id_ativo_origem": 2, "nivel": "BAIXA", "peso": 0.1}]
    app = FastAPI()

    @app.put("/ativos/9001/dependencias/2")
    def atualizar():
        dep = inventario.ativos[0].dependencias[0]
        dep["nivel"] = "ALTA"
        dep["peso"] = 0.4
        return {"ok": True}

    instalar_diario(app, lambda: inventario)
    with TestClient(app) as client:
        assert client.put("/ativos/9001/dependencias/2").status_code == 200
        diario = client.get("/diario").json()
        assert diario["total"] == 1
        evento = diario["eventos"][0]
        assert evento["tipo"] == "dependencia_atualizada"
        assert evento["alteracoes"]["nivel"] == {"anterior": "BAIXA", "novo": "ALTA"}
        assert evento["alteracoes"]["peso"] == {"anterior": 0.1, "novo": 0.4}


def test_diario_registra_status_e_cvss_modificados_na_mesma_operacao(tmp_path, monkeypatch):
    monkeypatch.setenv("CYBER_RISK_JOURNAL", str(tmp_path / "eventos.jsonl"))
    inventario = InventarioFake()
    inventario.ativos[0].vulnerabilidades[0].severidade = 6.4
    app = FastAPI()

    @app.patch("/ativos/9001/vulnerabilidades/501")
    def atualizar():
        v = inventario.ativos[0].vulnerabilidades[0]
        v.status = "EM_TRATAMENTO"
        v.severidade = 7.1
        return {"ok": True}

    instalar_diario(app, lambda: inventario)
    with TestClient(app) as client:
        assert client.patch("/ativos/9001/vulnerabilidades/501").status_code == 200
        eventos = client.get("/diario").json()["eventos"]
        assert {e["tipo"] for e in eventos} == {
            "tratamento_atualizado", "vulnerabilidade_atualizada"
        }
