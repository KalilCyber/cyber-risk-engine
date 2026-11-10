
from dominio.enums import Tratamento
from dominio.vulnerabilidades import Vulnerabilidade
from dominio.fabrica_ativos import FabricaAtivos

from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.persistencia_sqlalchemy import (
    PersistenciaSQLAlchemy,
)


def test_repositorio_preserva_tratamentos_individuais(tmp_path):

    engine = criar_engine_sqlite(
        tmp_path / "teste_repositorio_vulnerabilidades.db"
    )

    try:
        Base.metadata.create_all(engine)

        repositorio = PersistenciaSQLAlchemy(engine)

        def criar_vulnerabilidade(status):
            return Vulnerabilidade(
                id=501,
                descricao="Vulnerabilidade demonstrativa",
                categoria="CWE-79",
                severidade=6.4,
                status=status,
                cve_id="CVE-2026-99999"
            )

        notebook = FabricaAtivos.criar(
            "Notebook",
            7001,
            "Notebook de Teste",
            "Aline",
            "Cibersegurança",
            [criar_vulnerabilidade(Tratamento.ABERTO)],
            processador="Intel Core i5"
        )

        servidor = FabricaAtivos.criar(
            "Servidor",
            7002,
            "Servidor de Teste",
            "Aline",
            "Infraestrutura",
            [criar_vulnerabilidade(Tratamento.CORRIGIDA)],
            servico="Aplicação Interna"
        )

        # Salva os dois ativos com a mesma vulnerabilidade.
        repositorio.salvar([notebook, servidor])

        # Recupera os objetos pelo Repository.
        recuperados = {
            ativo.id: ativo
            for ativo in PersistenciaSQLAlchemy(engine).carregar()
        }

        assert len(recuperados) == 2

        vuln_notebook = recuperados[7001].vulnerabilidades[0]
        vuln_servidor = recuperados[7002].vulnerabilidades[0]

        assert vuln_notebook.status == Tratamento.ABERTO
        assert vuln_servidor.status == Tratamento.CORRIGIDA

        assert vuln_notebook is not vuln_servidor

        assert vuln_notebook.obter_severidade_efetiva() == 6.4
        assert vuln_servidor.obter_severidade_efetiva() == 0.0

        # Verifica também a substituição do inventário.
        repositorio.salvar([notebook])

        ativos_restantes = repositorio.carregar()

        assert len(ativos_restantes) == 1
        assert ativos_restantes[0].id == 7001
        assert len(ativos_restantes[0].vulnerabilidades) == 1

    finally:
        engine.dispose()
