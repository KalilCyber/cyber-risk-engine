
from dominio.enums import Tratamento
from dominio.vulnerabilidades import Vulnerabilidade

from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.sessao import criar_fabrica_sessoes

from infraestrutura.banco.modelos import (
    AtivoDB,
    AtivoVulnerabilidadeDB
)

from infraestrutura.banco.conversores import (
    vulnerabilidade_para_modelo,
    associacao_para_vulnerabilidade
)


def test_recuperar_tratamentos_independentes(tmp_path):
    engine = criar_engine_sqlite(
        tmp_path / "teste_conversao_vulnerabilidades.db"
    )

    try:
        Base.metadata.create_all(engine)
        FabricaSessoes = criar_fabrica_sessoes(engine)

        vulnerabilidade = Vulnerabilidade(
            id=501,
            descricao="Vulnerabilidade de teste",
            categoria="CWE-79",
            severidade=6.4,
            status=Tratamento.ABERTO,
            cve_id="CVE-2026-99999",
            cwe_id="CWE-79",
            cvss_vector="CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N",
            cvss_version="3.1"
        )

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

            modelo_vulnerabilidade = (
                vulnerabilidade_para_modelo(vulnerabilidade)
            )

            sessao.add_all([
                notebook,
                servidor,
                modelo_vulnerabilidade
            ])

            sessao.add_all([
                AtivoVulnerabilidadeDB(
                    ativo=notebook,
                    vulnerabilidade=modelo_vulnerabilidade,
                    status="ABERTO"
                ),
                AtivoVulnerabilidadeDB(
                    ativo=servidor,
                    vulnerabilidade=modelo_vulnerabilidade,
                    status="CORRIGIDA"
                )
            ])

        # Uma nova sessão comprova a recuperação do SQLite.
        with FabricaSessoes() as sessao:
            associacao_notebook = sessao.get(
                AtivoVulnerabilidadeDB,
                (7001, 501)
            )

            associacao_servidor = sessao.get(
                AtivoVulnerabilidadeDB,
                (7002, 501)
            )

            vuln_notebook = associacao_para_vulnerabilidade(
                associacao_notebook
            )

            vuln_servidor = associacao_para_vulnerabilidade(
                associacao_servidor
            )

            assert vuln_notebook.status == Tratamento.ABERTO
            assert vuln_servidor.status == Tratamento.CORRIGIDA

            assert vuln_notebook.id == vuln_servidor.id
            assert vuln_notebook.severidade == 6.4
            assert vuln_servidor.cve_id == "CVE-2026-99999"
            assert vuln_notebook.cwe_id == "CWE-79"
            assert vuln_notebook.cvss_version == "3.1"

            # Cada ativo recebe seu próprio objeto do domínio.
            assert vuln_notebook is not vuln_servidor

            # A regra de risco continua funcionando.
            assert vuln_notebook.obter_severidade_efetiva() == 6.4
            assert vuln_servidor.obter_severidade_efetiva() == 0.0

    finally:
        engine.dispose()
