
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from shutil import copy2, copyfileobj
from tempfile import TemporaryDirectory

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import URL

from infraestrutura.persistencia_json import Persistencia
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.persistencia_sqlalchemy import (
    PersistenciaSQLAlchemy,
)
from scripts.ensaio_migracao_json_sql import (
    fotografia,
    comparar_riscos,
)


RAIZ_PROJETO = Path(__file__).resolve().parents[1]


def calcular_hash(caminho):
    """Calcula a identificação SHA-256 de um arquivo."""
    hash_arquivo = sha256()

    with open(caminho, "rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(65536), b""):
            hash_arquivo.update(bloco)

    return hash_arquivo.hexdigest()


def migrar():
    origem = RAIZ_PROJETO / "ativos.json"

    if not origem.is_file():
        raise FileNotFoundError(
            "O arquivo ativos.json não foi encontrado."
        )

    carimbo = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    # O backup ficará fora do repositório Git.
    pasta_backup = (
        RAIZ_PROJETO.parent / "backups_cyber_risk_engine"
    )
    pasta_backup.mkdir(parents=True, exist_ok=True)

    backup = pasta_backup / f"ativos_pre_sql_{carimbo}.json"

    # O banco migrado ficará separado do banco principal.
    pasta_destino = RAIZ_PROJETO / "dados_sql"
    pasta_destino.mkdir(parents=True, exist_ok=True)

    destino = (
        pasta_destino / f"cyber_risk_migrado_{carimbo}.db"
    )

    # 1. Cria e verifica o backup.
    hash_original = calcular_hash(origem)
    copy2(origem, backup)

    if calcular_hash(backup) != hash_original:
        raise RuntimeError("O backup não confere com o JSON.")

    print(f"Backup criado: {backup}")

    # 2. Carrega os dados a partir do backup.
    ativos_originais = Persistencia(
        str(backup)
    ).carregar()

    dados_antes = fotografia(ativos_originais)

    contagens_esperadas = {
        "ativos": len(ativos_originais),
        "vulnerabilidades": len({
            vulnerabilidade.id
            for ativo in ativos_originais
            for vulnerabilidade in ativo.vulnerabilidades
        }),
        "ativo_vulnerabilidades": sum(
            len(ativo.vulnerabilidades)
            for ativo in ativos_originais
        ),
        "dependencias": sum(
            len(ativo.dependencias)
            for ativo in ativos_originais
        ),
    }

    # 3. Prepara o banco em um local temporário.
    with TemporaryDirectory(dir=pasta_destino) as pasta:
        banco_temporario = Path(pasta) / "preparacao.db"

        # Cria a estrutura usando Alembic.
        configuracao = Config(
            str(RAIZ_PROJETO / "alembic.ini")
        )
        configuracao.set_main_option(
            "script_location",
            str(RAIZ_PROJETO / "alembic")
        )

        url = URL.create(
            "sqlite+pysqlite",
            database=str(banco_temporario.resolve())
        )

        configuracao.set_main_option(
            "sqlalchemy.url",
            str(url).replace("%", "%%")
        )

        command.upgrade(configuracao, "head")

        engine = criar_engine_sqlite(banco_temporario)

        try:
            repositorio = PersistenciaSQLAlchemy(engine)

            # 4. Grava e recupera os ativos.
            repositorio.salvar(ativos_originais)
            ativos_recuperados = repositorio.carregar()

            if dados_antes != fotografia(ativos_recuperados):
                raise AssertionError(
                    "Os dados recuperados são diferentes do JSON."
                )

            # 5. Compara os resultados matemáticos.
            comparar_riscos(
                ativos_originais,
                ativos_recuperados
            )

            # 6. Confere contagens e integridade do SQLite.
            with engine.connect() as conexao:

                for tabela, esperado in contagens_esperadas.items():
                    quantidade = conexao.exec_driver_sql(
                        f"SELECT COUNT(*) FROM {tabela}"
                    ).scalar_one()

                    if quantidade != esperado:
                        raise AssertionError(
                            f"{tabela}: esperado {esperado}, "
                            f"encontrado {quantidade}"
                        )

                    print(f"{tabela}: {quantidade}")

                integridade = conexao.exec_driver_sql(
                    "PRAGMA integrity_check"
                ).scalar_one()

                if integridade != "ok":
                    raise RuntimeError(
                        f"Falha de integridade: {integridade}"
                    )

        finally:
            engine.dispose()

        # Impede finalizar se o JSON mudou durante a migração.
        if calcular_hash(origem) != hash_original:
            raise RuntimeError(
                "O JSON original mudou durante a migração. "
                "O novo banco não será publicado."
            )

        # 7. Publica o banco somente após as validações.
        # O modo 'xb' impede sobrescrever um banco existente.
        arquivo_criado = False

        try:
            with banco_temporario.open("rb") as entrada:
                with destino.open("xb") as saida:
                    arquivo_criado = True
                    copyfileobj(entrada, saida)

            if calcular_hash(destino) != calcular_hash(
                banco_temporario
            ):
                raise RuntimeError(
                    "A cópia do banco não foi concluída corretamente."
                )

        except Exception:
            if arquivo_criado:
                destino.unlink(missing_ok=True)
            raise

    print("\nMIGRAÇÃO PERSISTENTE VALIDADA!")
    print(f"Banco SQLite criado: {destino}")
    print(f"Backup do JSON: {backup}")
    print("O ativos.json original não foi modificado.")


if __name__ == "__main__":
    migrar()
