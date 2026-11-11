"""Migração explícita e validada do JSON para um SQLite persistente.

Executar: python -m scripts.migrar_json_para_sqlite [--origem ... --destino ... --backup-dir ...]
Nunca substitui um arquivo SQLite já existente. Não habilita SQL na API.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from shutil import copyfileobj
from tempfile import TemporaryDirectory

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.engine import URL

from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.persistencia_sqlalchemy import PersistenciaSQLAlchemy
from infraestrutura.persistencia_json import Persistencia
from scripts.ensaio_migracao_json_sql import comparar_riscos, fotografia

RAIZ_PROJETO = Path(__file__).resolve().parents[1]
TABELAS = (
    "ativos",
    "vulnerabilidades",
    "ativo_vulnerabilidades",
    "dependencias",
)


def calcular_hash(caminho: Path) -> str:
    hash_arquivo = sha256()
    with Path(caminho).open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(65536), b""):
            hash_arquivo.update(bloco)
    return hash_arquivo.hexdigest()


def _contagens(ativos) -> dict[str, int]:
    return {
        "ativos": len(ativos),
        "vulnerabilidades": len({
            vulnerabilidade.id
            for ativo in ativos
            for vulnerabilidade in ativo.vulnerabilidades
        }),
        "ativo_vulnerabilidades": sum(
            len(ativo.vulnerabilidades) for ativo in ativos
        ),
        "dependencias": sum(
            len(ativo.dependencias) for ativo in ativos
        ),
    }


def migrar(
    origem: str | Path | None = None,
    destino: str | Path | None = None,
    backup_dir: str | Path | None = None,
) -> dict:
    origem = Path(origem or RAIZ_PROJETO / "ativos.json").resolve()
    carimbo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destino = Path(
        destino or RAIZ_PROJETO / "dados_sql" / f"cyber_risk_migrado_{carimbo}.db"
    ).resolve()
    pasta_backup = Path(
        backup_dir or RAIZ_PROJETO.parent / "backups_cyber_risk_engine"
    ).resolve()

    if not origem.is_file():
        raise FileNotFoundError(f"Inventário JSON não encontrado: {origem}")
    if origem == destino:
        raise ValueError("Origem e destino precisam ser arquivos diferentes.")
    if destino.exists():
        raise FileExistsError(
            f"Destino já existe e não será sobrescrito: {destino}"
        )

    pasta_backup.mkdir(parents=True, exist_ok=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    backup = pasta_backup / f"ativos_pre_sql_{carimbo}.json"

    # Backup exclusivo, com conferência de integridade.
    hash_original = calcular_hash(origem)
    with origem.open("rb") as entrada, backup.open("xb") as saida:
        copyfileobj(entrada, saida)
    if calcular_hash(backup) != hash_original:
        raise RuntimeError("Backup JSON não confere com o original.")
    print(f"Backup criado: {backup}")

    ativos_antes = Persistencia(str(backup)).carregar()
    foto_antes = fotografia(ativos_antes)
    esperado = _contagens(ativos_antes)
    print(f"Ativos no JSON: {esperado['ativos']}")

    # Mesmo diretório/volume que o destino, para evitar caminhos dispersos.
    with TemporaryDirectory(dir=destino.parent) as pasta:
        banco_temporario = Path(pasta) / "preparacao.db"

        alembic_config = Config(str(RAIZ_PROJETO / "alembic.ini"))
        alembic_config.set_main_option(
            "script_location", str(RAIZ_PROJETO / "alembic")
        )
        url = URL.create(
            "sqlite+pysqlite", database=str(banco_temporario.resolve())
        )
        alembic_config.set_main_option(
            "sqlalchemy.url", str(url).replace("%", "%%")
        )
        command.upgrade(alembic_config, "head")

        engine = criar_engine_sqlite(banco_temporario)
        try:
            repositorio = PersistenciaSQLAlchemy(engine)
            repositorio.salvar(ativos_antes)
            ativos_depois = repositorio.carregar()

            if foto_antes != fotografia(ativos_depois):
                raise AssertionError("Dados divergentes entre JSON e SQLite.")
            comparar_riscos(ativos_antes, ativos_depois)

            with engine.connect() as conexao:
                for tabela in TABELAS:
                    quantidade = conexao.exec_driver_sql(
                        f"SELECT COUNT(*) FROM {tabela}"
                    ).scalar_one()
                    if quantidade != esperado[tabela]:
                        raise AssertionError(
                            f"{tabela}: {quantidade} != {esperado[tabela]}"
                        )
                    print(f"{tabela}: {quantidade}")

                integridade = conexao.exec_driver_sql(
                    "PRAGMA integrity_check"
                ).scalar_one()
                if integridade != "ok":
                    raise RuntimeError(f"Falha de integridade: {integridade}")
                violacoes_fk = conexao.exec_driver_sql(
                    "PRAGMA foreign_key_check"
                ).all()
                if violacoes_fk:
                    raise RuntimeError(
                        f"Violações de chaves estrangeiras: {violacoes_fk}"
                    )
                revisao_banco = conexao.exec_driver_sql(
                    "SELECT version_num FROM alembic_version"
                ).scalar_one()
                revisao_esperada = ScriptDirectory.from_config(
                    alembic_config
                ).get_current_head()
                if revisao_banco != revisao_esperada:
                    raise RuntimeError("Revisão Alembic inesperada no SQLite.")
        finally:
            engine.dispose()

        # Checa alterações concorrentes no JSON antes de publicar.
        if calcular_hash(origem) != hash_original:
            raise RuntimeError(
                "O JSON mudou durante a migração. Migração não publicada."
            )

        criado = False
        try:
            # Exclusivo: jamais substituir um SQLite existente.
            with banco_temporario.open("rb") as entrada:
                with destino.open("xb") as saida:
                    criado = True
                    copyfileobj(entrada, saida)
            if calcular_hash(destino) != calcular_hash(banco_temporario):
                raise RuntimeError("Cópia do banco incompleta.")
        except Exception:
            if criado:
                destino.unlink(missing_ok=True)
            raise

    print("\nMIGRAÇÃO PERSISTENTE VALIDADA!")
    print(f"Banco SQLite criado: {destino}")
    print(f"Backup do JSON: {backup}")
    print("Arquivo JSON original não foi modificado.")
    return {"destino": destino, "backup": backup, "contagens": esperado}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origem", type=Path, default=None)
    parser.add_argument("--destino", type=Path, default=None)
    parser.add_argument("--backup-dir", type=Path, default=None)
    args = parser.parse_args()
    migrar(origem=args.origem, destino=args.destino, backup_dir=args.backup_dir)


if __name__ == "__main__":
    main()
