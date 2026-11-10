
from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.sessao import criar_fabrica_sessoes
from infraestrutura.banco.modelos import AtivoDB


def test_chaves_estrangeiras_habilitadas(tmp_path):
    caminho = tmp_path / "teste_fk.db"
    engine = criar_engine_sqlite(caminho)

    try:
        FabricaSessoes = criar_fabrica_sessoes(engine)

        with FabricaSessoes() as sessao:
            resultado = sessao.connection().exec_driver_sql(
                "PRAGMA foreign_keys"
            ).scalar_one()

            assert resultado == 1

    finally:
        engine.dispose()


def test_salvar_e_recuperar_ativo_sqlite(tmp_path):
    caminho = tmp_path / "teste_ativos.db"
    engine = criar_engine_sqlite(caminho)

    try:
        # Cria as tabelas apenas no banco temporário
        Base.metadata.create_all(engine)

        FabricaSessoes = criar_fabrica_sessoes(engine)

        # Primeira sessão: cadastrar
        with FabricaSessoes() as sessao:
            ativo = AtivoDB(
                id=6001,
                nome="Notebook de Teste",
                responsavel="Teste",
                setor="Cibersegurança",
                tipo="Notebook",
                processador="Intel Core i5"
            )

            sessao.add(ativo)
            sessao.commit()

        # Segunda sessão: recuperar do banco
        with FabricaSessoes() as sessao:
            ativo_recuperado = sessao.get(
                AtivoDB,
                6001
            )

            assert ativo_recuperado is not None
            assert ativo_recuperado.nome == "Notebook de Teste"
            assert ativo_recuperado.processador == "Intel Core i5"

    finally:
        engine.dispose()
