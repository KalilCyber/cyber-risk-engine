
from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.sessao import criar_fabrica_sessoes

from infraestrutura.banco.modelos import (
    AtivoDB,
    DependenciaDB
)


def test_salvar_e_recuperar_dependencia(tmp_path):

    # Banco temporário e independente
    engine = criar_engine_sqlite(
        tmp_path / "teste_dependencias.db"
    )

    try:
        # Cria as tabelas no banco de teste
        Base.metadata.create_all(engine)

        FabricaSessoes = criar_fabrica_sessoes(engine)

        # Primeira transação: cadastrar os registros
        with FabricaSessoes.begin() as sessao:

            notebook = AtivoDB(
                id=7001,
                nome="Notebook de Teste",
                responsavel="Aline",
                setor="Cibersegurança",
                tipo="Notebook",
                processador="Intel Core i5"
            )

            servidor = AtivoDB(
                id=7002,
                nome="Servidor de Teste",
                responsavel="Aline",
                setor="Infraestrutura",
                tipo="Servidor",
                servico="Aplicação Interna"
            )

            dependencia = DependenciaDB(
                ativo_destino=notebook,
                ativo_origem=servidor,
                nivel="MODERADA",
                valor_nist=5,
                peso=0.25
            )

            sessao.add_all([
                notebook,
                servidor,
                dependencia
            ])

        # Segunda sessão: recuperar do banco
        with FabricaSessoes() as sessao:

            dependencia_recuperada = sessao.get(
                DependenciaDB,
                (7001, 7002)
            )

            assert dependencia_recuperada is not None

            assert dependencia_recuperada.ativo_destino_id == 7001
            assert dependencia_recuperada.ativo_origem_id == 7002

            assert dependencia_recuperada.nivel == "MODERADA"
            assert dependencia_recuperada.valor_nist == 5
            assert dependencia_recuperada.peso == 0.25

            # Verifica os relacionamentos ORM
            assert dependencia_recuperada.ativo_destino.nome == (
                "Notebook de Teste"
            )

            assert dependencia_recuperada.ativo_origem.nome == (
                "Servidor de Teste"
            )

            # Verifica a navegação inversa
            notebook_recuperado = sessao.get(AtivoDB, 7001)
            servidor_recuperado = sessao.get(AtivoDB, 7002)

            assert len(
                notebook_recuperado.dependencias_como_destino
            ) == 1

            assert len(
                servidor_recuperado.dependencias_como_origem
            ) == 1

    finally:
        engine.dispose()
