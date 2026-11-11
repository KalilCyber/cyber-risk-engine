
import pytest

from sqlalchemy import event

from dominio.enums import NivelDependencia
from dominio.fabrica_ativos import FabricaAtivos

from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite

from infraestrutura.banco.persistencia_sqlalchemy import (
    PersistenciaSQLAlchemy
)


def test_rollback_preserva_inventario_original(tmp_path):

    # Banco temporário exclusivo para o teste
    engine = criar_engine_sqlite(
        tmp_path / "teste_rollback.db"
    )

    try:
        Base.metadata.create_all(engine)

        repositorio = PersistenciaSQLAlchemy(engine)

        # 1. Criar os ativos originais
        notebook = FabricaAtivos.criar(
            "Notebook",
            7001,
            "Notebook Original",
            "Aline",
            "Cibersegurança",
            [],
            processador="Intel Core i5"
        )

        servidor = FabricaAtivos.criar(
            "Servidor",
            7002,
            "Servidor Original",
            "Aline",
            "Infraestrutura",
            [],
            servico="Aplicação Interna"
        )

        # 2. Salvar o inventário original
        repositorio.salvar([notebook, servidor])

        dados_anteriores = [
            ativo.to_dict()
            for ativo in repositorio.carregar()
        ]

        # 3. Preparar alterações válidas
        notebook.nome = "Notebook Modificado"

        notebook.adicionar_dependencia(
            7002,
            NivelDependencia.MODERADA
        )

        # 4. Simular falha durante um INSERT SQL
        def simular_falha(
            conn,
            cursor,
            statement,
            parameters,
            context,
            executemany
        ):
            comando = statement.lstrip().upper()

            if comando.startswith("INSERT INTO DEPENDENCIAS"):
                raise RuntimeError(
                    "Falha simulada durante a transação"
                )

        event.listen(
            engine,
            "before_cursor_execute",
            simular_falha
        )

        try:
            # 5. A gravação deverá falhar
            with pytest.raises(
                RuntimeError,
                match="Falha simulada"
            ):
                repositorio.salvar([notebook, servidor])

        finally:
            # Remove a simulação de erro
            event.remove(
                engine,
                "before_cursor_execute",
                simular_falha
            )

        # 6. Verificar se os dados anteriores sobreviveram
        dados_depois = [
            ativo.to_dict()
            for ativo in repositorio.carregar()
        ]

        assert dados_depois == dados_anteriores

        assert dados_depois[0]["nome"] == "Notebook Original"

        assert dados_depois[0]["dependencias"] == []

    finally:
        engine.dispose()
