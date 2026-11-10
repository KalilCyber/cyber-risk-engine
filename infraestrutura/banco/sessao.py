
from sqlalchemy.orm import sessionmaker


def criar_fabrica_sessoes(engine):
    """Cria uma fábrica de sessões SQLAlchemy."""

    return sessionmaker(
        bind=engine,
        expire_on_commit=False
    )
