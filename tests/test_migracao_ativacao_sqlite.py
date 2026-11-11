"""Testes da migração explícita e da seleção JSON/SQLite.

Execute após integrar o seletor no api/app.py para validar também o teste HTTP.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from dominio.enums import NivelDependencia, Tratamento
from dominio.fabrica_ativos import FabricaAtivos
from dominio.vulnerabilidades import Vulnerabilidade
from infraestrutura.seletor_repositorio import criar_repositorio_configurado
from scripts.migrar_json_para_sqlite import migrar

RAIZ = Path(__file__).resolve().parents[1]


def _sha256(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


@pytest.fixture
def json_exemplo(tmp_path):
    vuln_aberta = Vulnerabilidade(
        id=501,
        descricao="Vulnerabilidade de integração",
        categoria="CWE-79",
        severidade=6.4,
        status=Tratamento.ABERTO,
        cve_id="CVE-2026-99999",
    )
    vuln_corrigida = Vulnerabilidade(
        id=501,
        descricao="Vulnerabilidade de integração",
        categoria="CWE-79",
        severidade=6.4,
        status=Tratamento.CORRIGIDA,
        cve_id="CVE-2026-99999",
    )
    notebook = FabricaAtivos.criar(
        "Notebook", 7001, "Notebook de Teste", "Aline", "Cibersegurança",
        [vuln_aberta], processador="Intel Core i5",
    )
    servidor = FabricaAtivos.criar(
        "Servidor", 7002, "Servidor de Teste", "Aline", "Infraestrutura",
        [vuln_corrigida], servico="Aplicação Interna",
    )
    notebook.adicionar_dependencia(7002, NivelDependencia.MODERADA)

    origem = tmp_path / "inventario_exemplo.json"
    origem.write_text(
        json.dumps(
            [notebook.to_dict(), servidor.to_dict()],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return origem


def _migrar_exemplo(tmp_path, origem):
    return migrar(
        origem=origem,
        destino=tmp_path / "resultado_migrado.db",
        backup_dir=tmp_path / "backups",
    )


def test_migracao_persistente_cria_backup_e_preserva_json(tmp_path, json_exemplo):
    hash_antes = _sha256(json_exemplo)
    resultado = _migrar_exemplo(tmp_path, json_exemplo)

    assert resultado["destino"].is_file()
    assert resultado["backup"].is_file()
    assert _sha256(json_exemplo) == hash_antes == _sha256(resultado["backup"])
    assert resultado["contagens"] == {
        "ativos": 2,
        "vulnerabilidades": 1,
        "ativo_vulnerabilidades": 2,
        "dependencias": 1,
    }


def test_migracao_nao_sobrescreve_banco(tmp_path, json_exemplo):
    primeiro = _migrar_exemplo(tmp_path, json_exemplo)
    hash_antes = _sha256(primeiro["destino"])

    with pytest.raises(FileExistsError, match="não será sobrescrito"):
        _migrar_exemplo(tmp_path, json_exemplo)

    assert _sha256(primeiro["destino"]) == hash_antes


def test_seletor_json_continua_funcionando(tmp_path, json_exemplo, monkeypatch):
    monkeypatch.setenv("CYBER_RISK_STORAGE", "json")
    monkeypatch.setenv("CYBER_RISK_DATA", str(json_exemplo))
    repositorio = criar_repositorio_configurado(RAIZ)
    assert sorted(ativo.id for ativo in repositorio.carregar()) == [7001, 7002]


def test_seletor_sqlite_carrega_dados_migrados(tmp_path, json_exemplo, monkeypatch):
    resultado = _migrar_exemplo(tmp_path, json_exemplo)
    monkeypatch.setenv("CYBER_RISK_STORAGE", "sqlite")
    monkeypatch.setenv("CYBER_RISK_DB", str(resultado["destino"]))
    repositorio = criar_repositorio_configurado(RAIZ)
    ativos = {ativo.id: ativo for ativo in repositorio.carregar()}
    assert len(ativos) == 2
    assert ativos[7001].dependencias[0]["id_ativo_origem"] == 7002
    assert ativos[7001].vulnerabilidades[0].status == Tratamento.ABERTO
    assert ativos[7002].vulnerabilidades[0].status == Tratamento.CORRIGIDA


def test_sqlite_inexistente_nao_cria_banco_vazio(tmp_path, monkeypatch):
    banco = tmp_path / "inexistente.db"
    monkeypatch.setenv("CYBER_RISK_STORAGE", "sqlite")
    monkeypatch.setenv("CYBER_RISK_DB", str(banco))
    with pytest.raises(FileNotFoundError, match="Banco SQLite inexistente"):
        criar_repositorio_configurado(RAIZ)
    assert not banco.exists()


def test_api_http_lê_dados_do_sqlite(tmp_path, json_exemplo):
    """Processo separado evita modificar o estado global da API nos outros testes."""
    resultado = _migrar_exemplo(tmp_path, json_exemplo)
    ambiente = os.environ.copy()
    ambiente["CYBER_RISK_STORAGE"] = "sqlite"
    ambiente["CYBER_RISK_DB"] = str(resultado["destino"])
    ambiente["CYBER_RISK_JOURNAL"] = str(tmp_path / "diario_teste.jsonl")
    ambiente["PYTHONIOENCODING"] = "utf-8"
    programa = (
        "from fastapi.testclient import TestClient\n"
        "from api.app import app\n"
        "r = TestClient(app).get('/ativos')\n"
        "assert r.status_code == 200, r.text\n"
        "ids = sorted(item['id'] for item in r.json())\n"
        "assert ids == [7001, 7002], ids\n"
        "print('API SQLite OK:', ids)\n"
    )
    processo = subprocess.run(
        [sys.executable, "-c", programa],
        cwd=RAIZ,
        env=ambiente,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=45,
        check=False,
    )
    assert processo.returncode == 0, (
        processo.stdout + "\n" + processo.stderr
    )
