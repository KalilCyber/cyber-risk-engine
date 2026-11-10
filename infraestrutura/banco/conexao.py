
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_BANCO = RAIZ_PROJETO / "cyber_risk.db"


def criar_engine_sqlite(caminho_banco=CAMINHO_BANCO):
    """Cria a conexão SQLAlchemy com o SQLite."""

    caminho = str(caminho_banco)

    if caminho != ":memory:":
        caminho = str(Path(caminho).resolve())

    url = URL.create(
        "sqlite+pysqlite",
        database=caminho
    )

    engine = create_engine(url)

    @event.listens_for(engine, "connect")
    def ativar_chaves_estrangeiras(conexao_dbapi, _):
        cursor = conexao_dbapi.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()

    return engine
