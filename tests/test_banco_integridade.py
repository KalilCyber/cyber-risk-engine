
import pytest

from sqlalchemy import insert, select, func
from sqlalchemy.exc import IntegrityError

from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite

from infraestrutura.banco.modelos import (
    AtivoDB,
    VulnerabilidadeDB,
    AtivoVulnerabilidadeDB,
    DependenciaDB,
)


@pytest.fixture
def banco_integridade(tmp_path):
    """Prepara um SQLite temporário para cada teste."""

    engine = criar_engine_sqlite(
        tmp_path / "teste_integridade.db"
    )

    try:
        Base.metadata.create_all(engine)

        with engine.begin() as conexao:

            # Ativo 1
            conexao.execute(
                insert(AtivoDB).values(
                    id=7001,
                    nome="Notebook de Teste",
                    responsavel="Aline",
                    setor="Cibersegurança",
                    tipo="Notebook",
                    processador="Intel Core i5"
                )
            )

            # Ativo 2
            conexao.execute(
                insert(AtivoDB).values(
                    id=7002,
                    nome="Servidor de Teste",
                    responsavel="Aline",
                    setor="Infraestrutura",
                    tipo="Servidor",
                    servico="Aplicação Interna"
                )
            )

            # Vulnerabilidade de teste
            conexao.execute(
                insert(VulnerabilidadeDB).values(
                    id=501,
                    descricao="Vulnerabilidade demonstrativa",
                    categoria="CWE-79",
                    severidade=6.4
                )
            )

        yield engine

    finally:
        engine.dispose()


def test_rejeitar_chave_estrangeira_inexistente(
    banco_integridade
):
    """Não permite associar vulnerabilidade a ativo inexistente."""

    with pytest.raises(IntegrityError):

        with banco_integridade.begin() as conexao:
            conexao.execute(
                insert(AtivoVulnerabilidadeDB).values(
                    ativo_id=9999,
                    vulnerabilidade_id=501,
                    status="ABERTO"
                )
            )

    with banco_integridade.connect() as conexao:
        quantidade = conexao.scalar(
            select(func.count()).select_from(
                AtivoVulnerabilidadeDB
            )
        )

        assert quantidade == 0


def test_rejeitar_associacao_duplicada(banco_integridade):
    """O mesmo par ativo-vulnerabilidade não pode se repetir."""

    with banco_integridade.begin() as conexao:
        conexao.execute(
            insert(AtivoVulnerabilidadeDB).values(
                ativo_id=7001,
                vulnerabilidade_id=501,
                status="ABERTO"
            )
        )

    with pytest.raises(IntegrityError):

        with banco_integridade.begin() as conexao:
            conexao.execute(
                insert(AtivoVulnerabilidadeDB).values(
                    ativo_id=7001,
                    vulnerabilidade_id=501,
                    status="CORRIGIDA"
                )
            )

    with banco_integridade.connect() as conexao:
        quantidade = conexao.scalar(
            select(func.count()).select_from(
                AtivoVulnerabilidadeDB
            )
        )

        assert quantidade == 1


@pytest.mark.parametrize(
    "origem_id, peso",
    [
        (7001, 0.25),
        (7002, 1.0),
    ],
    ids=[
        "autorreferencia",
        "peso_igual_a_um",
    ]
)
def test_rejeitar_dependencia_invalida(
    banco_integridade,
    origem_id,
    peso
):
    """Valida as restrições CHECK da tabela dependencias."""

    with pytest.raises(IntegrityError):

        with banco_integridade.begin() as conexao:
            conexao.execute(
                insert(DependenciaDB).values(
                    ativo_destino_id=7001,
                    ativo_origem_id=origem_id,
                    nivel="MODERADA",
                    valor_nist=5,
                    peso=peso
                )
            )

    with banco_integridade.connect() as conexao:
        quantidade = conexao.scalar(
            select(func.count()).select_from(
                DependenciaDB
            )
        )

        assert quantidade == 0
