
import pytest

from dominio.fabrica_ativos import FabricaAtivos
from infraestrutura.banco.base import Base
from infraestrutura.banco.conexao import criar_engine_sqlite
from infraestrutura.banco.sessao import criar_fabrica_sessoes
from infraestrutura.banco.modelos import AtivoDB
from infraestrutura.banco.conversores import (
    ativo_para_modelo,
    modelo_para_ativo
)


@pytest.mark.parametrize(
    "tipo, campo, valor",
    [
        ("Notebook", "processador", "Intel Core i5"),
        ("Servidor", "servico", "Aplicação Interna"),
        ("Roteador", "endereco_ip", "192.168.1.1"),
        ("AplicacaoWeb", "url", "https://exemplo.com")
    ]
)
def test_conversao_ativo_sqlite(
    tmp_path, tipo, campo, valor
):
    engine = criar_engine_sqlite(
        tmp_path / "teste_conversao.db"
    )

    try:
        Base.metadata.create_all(engine)

        FabricaSessoes = criar_fabrica_sessoes(engine)

        # Cria um objeto real do domínio
        ativo_original = FabricaAtivos.criar(
            tipo,
            8001,
            "Ativo de Teste",
            "Aline",
            "Cibersegurança",
            [],
            **{campo: valor}
        )

        # Converte e salva no SQLite
        with FabricaSessoes.begin() as sessao:
            modelo = ativo_para_modelo(ativo_original)
            sessao.add(modelo)

        # Recupera e reconstrói o objeto do domínio
        with FabricaSessoes() as sessao:
            modelo_recuperado = sessao.get(AtivoDB, 8001)

            assert modelo_recuperado is not None

            ativo_recuperado = modelo_para_ativo(
                modelo_recuperado
            )

            assert type(ativo_recuperado) is type(ativo_original)

            assert ativo_recuperado.to_dict() == (
                ativo_original.to_dict()
            )

    finally:
        engine.dispose()

