
from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.sessao import criar_fabrica_sessoes

from infraestrutura.banco.modelos import (
    AtivoDB,
    VulnerabilidadeDB,
    AtivoVulnerabilidadeDB
)


def test_vulnerabilidade_compartilhada_com_status_independentes(tmp_path):
    # Banco isolado para este teste
    engine = criar_engine_sqlite(
        tmp_path / "teste_associacoes.db"
    )

    try:
        Base.metadata.create_all(engine)
        FabricaSessoes = criar_fabrica_sessoes(engine)

        # Primeira transação: cadastro dos dados
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

            vulnerabilidade = VulnerabilidadeDB(
                id=501,
                descricao="Vulnerabilidade demonstrativa",
                categoria="CWE-79",
                severidade=6.4,
                cve_id="CVE-TESTE"
            )

            sessao.add_all([
                notebook,
                servidor,
                vulnerabilidade
            ])

            sessao.add_all([
                AtivoVulnerabilidadeDB(
                    ativo=notebook,
                    vulnerabilidade=vulnerabilidade,
                    status="ABERTO"
                ),
                AtivoVulnerabilidadeDB(
                    ativo=servidor,
                    vulnerabilidade=vulnerabilidade,
                    status="CORRIGIDA"
                )
            ])

        # Segunda sessão: verificar a persistência
        with FabricaSessoes() as sessao:
            associacao_notebook = sessao.get(
                AtivoVulnerabilidadeDB,
                (7001, 501)
            )

            associacao_servidor = sessao.get(
                AtivoVulnerabilidadeDB,
                (7002, 501)
            )

            assert associacao_notebook is not None
            assert associacao_servidor is not None

            assert associacao_notebook.status == "ABERTO"
            assert associacao_servidor.status == "CORRIGIDA"

            assert associacao_notebook.ativo.nome == (
                "Notebook de Teste"
            )

            assert associacao_servidor.vulnerabilidade.cve_id == (
                "CVE-TESTE"
            )

            vulnerabilidade = sessao.get(
                VulnerabilidadeDB,
                501
            )

            assert len(vulnerabilidade.associacoes_ativos) == 2

    finally:
        engine.dispose()
