
import pytest

from dominio.enums import NivelDependencia, Tratamento
from dominio.fabrica_ativos import FabricaAtivos
from dominio.vulnerabilidades import Vulnerabilidade

from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.persistencia_sqlalchemy import (
    PersistenciaSQLAlchemy,
)


def criar_ativos_de_teste():
    vulnerabilidade = Vulnerabilidade(
        id=501,
        descricao="Vulnerabilidade demonstrativa",
        categoria="CWE-79",
        severidade=6.4,
        status=Tratamento.ABERTO,
        cve_id="CVE-2026-99999"
    )

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
        [vulnerabilidade],
        servico="Aplicação Interna"
    )

    notebook.adicionar_dependencia(
        7002,
        NivelDependencia.MODERADA
    )

    return notebook, servidor


def test_salvar_e_carregar_inventario_completo(tmp_path):
    engine = criar_engine_sqlite(
        tmp_path / "inventario_completo.db"
    )

    try:
        Base.metadata.create_all(engine)

        repositorio = PersistenciaSQLAlchemy(engine)
        notebook, servidor = criar_ativos_de_teste()

        repositorio.salvar([notebook, servidor])

        recuperados = {
            ativo.id: ativo
            for ativo in repositorio.carregar()
        }

        assert len(recuperados) == 2

        assert recuperados[7001].to_dict() == (
            notebook.to_dict()
        )

        assert recuperados[7002].to_dict() == (
            servidor.to_dict()
        )

        assert (
            recuperados[7002]
            .vulnerabilidades[0]
            .status == Tratamento.ABERTO
        )

    finally:
        engine.dispose()


def test_dependencia_invalida_preserva_dados(tmp_path):
    engine = criar_engine_sqlite(
        tmp_path / "inventario_protegido.db"
    )

    try:
        Base.metadata.create_all(engine)

        repositorio = PersistenciaSQLAlchemy(engine)
        notebook, servidor = criar_ativos_de_teste()

        repositorio.salvar([notebook, servidor])

        # Fotografia anterior à tentativa inválida.
        dados_anteriores = [
            ativo.to_dict()
            for ativo in repositorio.carregar()
        ]

        # Simula um vínculo com um ativo inexistente.
        notebook.dependencias = [
            {
                "id_ativo_origem": 9999,
                "nivel": "MODERADA",
                "valor_nist": 5,
                "peso": 0.25
            }
        ]

        with pytest.raises(ValueError, match="origem"):
            repositorio.salvar([notebook, servidor])

        # O banco deve conservar a versão anterior.
        dados_depois = [
            ativo.to_dict()
            for ativo in repositorio.carregar()
        ]

        assert dados_depois == dados_anteriores

    finally:
        engine.dispose()
