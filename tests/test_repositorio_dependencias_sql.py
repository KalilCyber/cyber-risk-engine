
from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.sessao import criar_fabrica_sessoes

from infraestrutura.banco.modelos import (
    AtivoDB,
    DependenciaDB
)

from infraestrutura.banco.persistencia_sqlalchemy import (
    PersistenciaSQLAlchemy
)


def test_carregar_dependencias_pelo_repositorio(tmp_path):

    engine = criar_engine_sqlite(
        tmp_path / "teste_repo_dependencias.db"
    )

    try:
        Base.metadata.create_all(engine)

        FabricaSessoes = criar_fabrica_sessoes(engine)

        # Insere os registros diretamente no ORM.
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

        # Recupera os objetos através do Repository.
        repositorio = PersistenciaSQLAlchemy(engine)

        ativos = repositorio.carregar()

        assert len(ativos) == 2

        ativos_por_id = {
            ativo.id: ativo
            for ativo in ativos
        }

        notebook_recuperado = ativos_por_id[7001]
        servidor_recuperado = ativos_por_id[7002]

        assert notebook_recuperado.nome == (
            "Notebook de Teste"
        )

        assert servidor_recuperado.nome == (
            "Servidor de Teste"
        )

        # Confirma a reconstrução da dependência.
        assert notebook_recuperado.dependencias == [
            {
                "id_ativo_origem": 7002,
                "nivel": "MODERADA",
                "valor_nist": 5,
                "peso": 0.25
            }
        ]

        # O servidor não depende de outro ativo.
        assert servidor_recuperado.dependencias == []

    finally:
        engine.dispose()
