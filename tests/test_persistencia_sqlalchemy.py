
from dominio.fabrica_ativos import FabricaAtivos

from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite

from infraestrutura.banco.persistencia_sqlalchemy import (
    PersistenciaSQLAlchemy,
)


def test_salvar_carregar_e_substituir_inventario_sqlite(tmp_path):

    engine = criar_engine_sqlite(
        tmp_path / "teste_repositorio.db"
    )

    try:
        Base.metadata.create_all(engine)

        repositorio = PersistenciaSQLAlchemy(engine)

        notebook = FabricaAtivos.criar(
            "Notebook",
            7001,
            "Notebook de Teste",
            "Aline",
            "Cibersegurança",
            [],
            processador="Intel Core i5"
        )

        servidor = FabricaAtivos.criar(
            "Servidor",
            7002,
            "Servidor de Teste",
            "Aline",
            "Infraestrutura",
            [],
            servico="Aplicação Interna"
        )

        # Salva os dois ativos.
        repositorio.salvar([notebook, servidor])

        # Carrega por uma nova instância do Repository.
        outro_repositorio = PersistenciaSQLAlchemy(engine)

        ativos = outro_repositorio.carregar()

        assert len(ativos) == 2
        assert ativos[0].to_dict() == notebook.to_dict()
        assert ativos[1].to_dict() == servidor.to_dict()

        # Substitui o inventário por apenas um ativo.
        repositorio.salvar([servidor])

        ativos_atualizados = outro_repositorio.carregar()

        assert len(ativos_atualizados) == 1
        assert ativos_atualizados[0].id == 7002

    finally:
        engine.dispose()
