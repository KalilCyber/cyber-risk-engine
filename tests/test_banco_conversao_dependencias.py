
from dominio.ativos import Notebook

from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.sessao import criar_fabrica_sessoes

from infraestrutura.banco.modelos import (
    AtivoDB,
    DependenciaDB
)

from infraestrutura.banco.conversores import modelo_para_ativo


def test_reconstruir_dependencias_do_sqlite(tmp_path):

    engine = criar_engine_sqlite(
        tmp_path / "teste_conversao_dependencias.db"
    )

    try:
        Base.metadata.create_all(engine)
        FabricaSessoes = criar_fabrica_sessoes(engine)

        # Primeira transação: salvar os registros ORM
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

        # Segunda sessão: recuperar o objeto do domínio
        with FabricaSessoes() as sessao:

            modelo = sessao.get(AtivoDB, 7001)

            ativo_recuperado = modelo_para_ativo(modelo)

            assert isinstance(ativo_recuperado, Notebook)
            assert ativo_recuperado.id == 7001

            assert ativo_recuperado.dependencias == [
                {
                    "id_ativo_origem": 7002,
                    "nivel": "MODERADA",
                    "valor_nist": 5,
                    "peso": 0.25
                }
            ]

    finally:
        engine.dispose()
