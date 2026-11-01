
import numpy as np
import pytest

from dominio.enums import Tratamento
from dominio.fabrica_ativos import FabricaAtivos
from dominio.vulnerabilidades import Vulnerabilidade
from servicos.inventario import Inventario
from servicos.modelo_risco import ModeloRisco


@pytest.fixture
def inventario_risco():
    """
    Cenário isolado com quatro ativos.
    Não utiliza nem modifica ativos.json.
    """

    vuln_acer = Vulnerabilidade(
        id=701,
        descricao="Falha XSS",
        categoria="CWE-79",
        severidade=6.4,
        status=Tratamento.ABERTO
    )

    vuln_roteador = Vulnerabilidade(
        id=702,
        descricao="SQL Injection",
        categoria="CWE-89",
        severidade=8.7,
        status=Tratamento.CORRIGIDA
    )

    vuln_servidor = Vulnerabilidade(
        id=703,
        descricao="Path Traversal",
        categoria="CWE-22",
        severidade=7.1,
        status=Tratamento.EM_TRATAMENTO
    )

    vuln_alienware = Vulnerabilidade(
        id=704,
        descricao="Falha de segurança",
        categoria="CWE-1327",
        severidade=4.3,
        status=Tratamento.ABERTO
    )

    acer = FabricaAtivos.criar(
        "Notebook", 7, "Notebook Acer Nitro",
        "Aline", "Cibersegurança",
        [vuln_acer],
        processador="Intel Core i5"
    )

    roteador = FabricaAtivos.criar(
        "Roteador", 23, "Roteador Principal",
        "Kalil", "Cibersegurança",
        [vuln_roteador],
        endereco_ip="192.168.0.1"
    )

    servidor = FabricaAtivos.criar(
        "Servidor", 31, "Servidor Principal",
        "Jones", "Cibersegurança",
        [vuln_servidor],
        servico="Banco de Dados"
    )

    alienware = FabricaAtivos.criar(
        "Notebook", 4, "Notebook Alienware",
        "Gabriel", "Cibersegurança",
        [vuln_alienware],
        processador="Ryzen 7 5700x"
    )

    # Acer depende do Roteador
    acer.dependencias = [
        {"id_ativo_origem": 23, "peso": 0.25}
    ]

    # Roteador depende do Servidor
    roteador.dependencias = [
        {"id_ativo_origem": 31, "peso": 0.10}
    ]

    return Inventario(
        [acer, roteador, servidor, alienware]
    )


def test_dimensoes_matrizes(inventario_risco):
    modelo = ModeloRisco(inventario_risco)
    modelo.calcular_risco_efetivo()

    assert modelo.matriz_m.shape == (4, 4)
    assert modelo.vetor_v.shape == (4,)
    assert modelo.matriz_a.shape == (4, 4)
    assert modelo.matriz_sistema.shape == (4, 4)


def test_risco_proprio(inventario_risco):
    modelo = ModeloRisco(inventario_risco)

    resultado = modelo.calcular_risco_proprio()

    esperado = [6.4, 0.0, 7.1, 4.3]

    np.testing.assert_allclose(
        resultado, esperado, atol=1e-8
    )


def test_vulnerabilidade_corrigida(
    inventario_risco
):
    modelo = ModeloRisco(inventario_risco)
    modelo.calcular_risco_efetivo()

    roteador = inventario_risco.buscar_por_id(23)
    vulnerabilidade = roteador.vulnerabilidades[0]

    # Preserva o CVSS original
    assert vulnerabilidade.severidade == 8.7

    # Mas elimina sua contribuição própria
    assert modelo.vetor_b[1] == pytest.approx(0.0)


def test_matriz_dependencias(inventario_risco):
    modelo = ModeloRisco(inventario_risco)

    resultado = modelo.construir_matriz_a()

    esperado = np.array([
        [0.0, 0.25, 0.0, 0.0],
        [0.0, 0.0, 0.10, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0]
    ])

    np.testing.assert_allclose(
        resultado, esperado, atol=1e-8
    )


def test_risco_efetivo(inventario_risco):
    modelo = ModeloRisco(inventario_risco)

    resultado = modelo.calcular_risco_efetivo()

    esperado = [6.5775, 0.71, 7.1, 4.3]

    np.testing.assert_allclose(
        resultado, esperado, atol=1e-8
    )


def test_equacao_matricial(inventario_risco):
    modelo = ModeloRisco(inventario_risco)

    vetor_x = modelo.calcular_risco_efetivo()

    # Verifica (I - A)x = b
    resultado = modelo.matriz_sistema @ vetor_x

    np.testing.assert_allclose(
        resultado, modelo.vetor_b, atol=1e-8
    )


def test_inventario_vazio():
    modelo = ModeloRisco(Inventario([]))

    resultado = modelo.calcular_risco_efetivo()

    assert len(resultado) == 0


def test_dependencia_inexistente(inventario_risco):
    acer = inventario_risco.buscar_por_id(7)

    acer.dependencias = [
        {"id_ativo_origem": 99999, "peso": 0.25}
    ]

    modelo = ModeloRisco(inventario_risco)

    with pytest.raises(ValueError):
        modelo.calcular_risco_efetivo()


def test_matriz_singular(inventario_risco):
    """
    Força um sistema singular artificialmente
    para verificar a proteção matemática.

    Não representa um cadastro válido.
    """

    acer = inventario_risco.buscar_por_id(7)
    roteador = inventario_risco.buscar_por_id(23)
    servidor = inventario_risco.buscar_por_id(31)
    alienware = inventario_risco.buscar_por_id(4)

    acer.dependencias = [
        {"id_ativo_origem": 23, "peso": 1.0}
    ]

    roteador.dependencias = [
        {"id_ativo_origem": 7, "peso": 1.0}
    ]

    servidor.dependencias = []
    alienware.dependencias = []

    modelo = ModeloRisco(inventario_risco)

    with pytest.raises(ValueError):
        modelo.calcular_risco_efetivo()
