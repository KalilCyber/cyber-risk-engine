
import pytest

from dominio.fabrica_ativos import FabricaAtivos
from infraestrutura.persistencia_json import Persistencia
from servicos.inventario import Inventario


@pytest.fixture
def inventario_teste(tmp_path):
    """
    Cria um inventário isolado para cada teste.
    Não utiliza o ativos.json original.
    """
    arquivo = tmp_path / "inventario_teste.json"

    repositorio = Persistencia(str(arquivo))

    return Inventario(
        [],
        repositorio=repositorio
    )


@pytest.fixture
def notebook_teste():
    return FabricaAtivos.criar(
        "Notebook",
        7,
        "Notebook Acer Nitro",
        "Aline",
        "Cibersegurança",
        [],
        processador="Intel Core i5"
    )


def test_cadastrar_ativo(
    inventario_teste,
    notebook_teste
):
    inventario_teste.cadastrar_ativo(notebook_teste)

    assert len(inventario_teste.listar_ativos()) == 1
    assert inventario_teste.buscar_por_id(7) is not None


def test_rejeitar_id_duplicado(
    inventario_teste,
    notebook_teste
):
    inventario_teste.cadastrar_ativo(notebook_teste)

    outro_notebook = FabricaAtivos.criar(
        "Notebook",
        7,
        "Outro Notebook",
        "Gabriel",
        "TI",
        [],
        processador="Ryzen 7"
    )

    with pytest.raises(ValueError):
        inventario_teste.cadastrar_ativo(outro_notebook)

    assert len(inventario_teste.listar_ativos()) == 1


def test_buscar_ativo_inexistente(inventario_teste):
    resultado = inventario_teste.buscar_por_id(99999)

    assert resultado is None


def test_atualizar_nome(
    inventario_teste,
    notebook_teste
):
    inventario_teste.cadastrar_ativo(notebook_teste)

    inventario_teste.atualizar_ativo(
        7,
        nome="Notebook Acer Atualizado"
    )

    ativo = inventario_teste.buscar_por_id(7)

    assert ativo.nome == "Notebook Acer Atualizado"


def test_remover_ativo(
    inventario_teste,
    notebook_teste
):
    inventario_teste.cadastrar_ativo(notebook_teste)

    inventario_teste.remover_ativo(7)

    assert inventario_teste.buscar_por_id(7) is None
    assert inventario_teste.listar_ativos() == []


def test_atualizacao_atomica(
    inventario_teste,
    notebook_teste
):
    """
    Uma atualização inválida não pode modificar
    parcialmente os dados do ativo.
    """
    inventario_teste.cadastrar_ativo(notebook_teste)

    with pytest.raises(ValueError):
        inventario_teste.atualizar_ativo(
            7,
            nome="Nome Alterado",
            responsavel="-2"
        )

    ativo = inventario_teste.buscar_por_id(7)

    assert ativo.nome == "Notebook Acer Nitro"
    assert ativo.responsavel == "Aline"


def test_salvar_e_recarregar_inventario(
    inventario_teste,
    notebook_teste
):
    inventario_teste.cadastrar_ativo(notebook_teste)

    inventario_teste.salvar()

    ativos_recuperados = (
        inventario_teste.repositorio.carregar()
    )

    assert len(ativos_recuperados) == 1

    ativo = ativos_recuperados[0]

    assert ativo.id == 7
    assert ativo.nome == "Notebook Acer Nitro"
    assert ativo.processador == "Intel Core i5"
