"""Seleciona o backend de persistência sem mudar as regras do Inventario.

CYBER_RISK_STORAGE=json (padrão) ou sqlite.
Banco SQL *nunca* é criado nem migrado automaticamente na inicialização da API.
"""
from __future__ import annotations

import os
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.persistencia_sqlalchemy import PersistenciaSQLAlchemy
from infraestrutura.persistencia_json import Persistencia


_TABELAS = {
    "alembic_version",
    "ativos",
    "vulnerabilidades",
    "ativo_vulnerabilidades",
    "dependencias",
}


def _revisao_esperada(raiz: Path) -> str:
    config = Config(str(raiz / "alembic.ini"))
    config.set_main_option("script_location", str(raiz / "alembic"))
    heads = ScriptDirectory.from_config(config).get_heads()
    if len(heads) != 1:
        raise RuntimeError(
            "Esperada uma única revisão head do Alembic; "
            f"revisões encontradas: {heads}."
        )
    return heads[0]


def _validar_banco_sqlite(engine: Engine, raiz: Path) -> None:
    with engine.connect() as conexao:
        tabelas = set(inspect(conexao).get_table_names())
        ausentes = _TABELAS - tabelas
        if ausentes:
            raise RuntimeError(
                "SQLite não está migrado; tabelas ausentes: "
                + ", ".join(sorted(ausentes))
            )
        revisao = conexao.exec_driver_sql(
            "SELECT version_num FROM alembic_version"
        ).scalar_one_or_none()
        esperada = _revisao_esperada(raiz)
        if revisao != esperada:
            raise RuntimeError(
                "Revisão SQLite incompatível com as migrações do projeto: "
                f"banco={revisao!r}, esperada={esperada!r}."
            )
        if conexao.exec_driver_sql("PRAGMA foreign_keys").scalar_one() != 1:
            raise RuntimeError("SQLite sem PRAGMA foreign_keys=ON.")


def criar_repositorio_configurado(raiz_projeto: Path):
    """Retorna um RepositorioAtivos (JSON por padrão, SQLite por opção)."""
    raiz = Path(raiz_projeto).resolve()
    modo = os.getenv("CYBER_RISK_STORAGE", "json").strip().lower()

    if modo == "json":
        caminho = Path(
            os.getenv("CYBER_RISK_DATA", str(raiz / "ativos.json"))
        ).resolve()
        return Persistencia(str(caminho))

    if modo != "sqlite":
        raise ValueError(
            "CYBER_RISK_STORAGE inválida. Use 'json' ou 'sqlite'."
        )

    caminho_banco = Path(
        os.getenv("CYBER_RISK_DB", str(raiz / "cyber_risk.db"))
    ).resolve()
    if not caminho_banco.is_file():
        raise FileNotFoundError(
            "Banco SQLite inexistente: " + str(caminho_banco)
            + ". Execute primeiro a migração explícita."
        )

    engine = criar_engine_sqlite(caminho_banco)
    try:
        _validar_banco_sqlite(engine, raiz)
    except Exception:
        engine.dispose()
        raise
    return PersistenciaSQLAlchemy(engine)
