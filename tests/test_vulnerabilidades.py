
import pytest

from dominio.vulnerabilidades import Vulnerabilidade
from dominio.enums import Tratamento


@pytest.fixture
def vulnerabilidade_teste():
    return Vulnerabilidade(
        id=501,
        descricao="SQL Injection",
        categoria="CWE-89",
        severidade=7.1,
        status=Tratamento.ABERTO
    )


def test_criar_vulnerabilidade(vulnerabilidade_teste):
    assert vulnerabilidade_teste.id == 501
    assert vulnerabilidade_teste.severidade == 7.1
    assert vulnerabilidade_teste.status == Tratamento.ABERTO


def test_rejeitar_severidade_negativa():
    with pytest.raises(ValueError):
        Vulnerabilidade(
            id=502,
            descricao="XSS",
            categoria="CWE-79",
            severidade=-2,
            status=Tratamento.ABERTO
        )


def test_rejeitar_severidade_acima_de_10():
    with pytest.raises(ValueError):
        Vulnerabilidade(
            id=503,
            descricao="SQL Injection",
            categoria="CWE-89",
            severidade=11,
            status=Tratamento.ABERTO
        )


def test_corrigida_zera_risco(vulnerabilidade_teste):
    vulnerabilidade_teste.atualizar(
        status=Tratamento.CORRIGIDA
    )

    assert vulnerabilidade_teste.severidade == 7.1
    assert vulnerabilidade_teste.obter_severidade_efetiva() == 0


def test_em_tratamento_mantem_severidade(
    vulnerabilidade_teste
):
    vulnerabilidade_teste.atualizar(
        status=Tratamento.EM_TRATAMENTO
    )

    assert vulnerabilidade_teste.obter_severidade_efetiva() == 7.1


def test_atualizacao_atomica_vulnerabilidade(
    vulnerabilidade_teste
):
    with pytest.raises(ValueError):
        vulnerabilidade_teste.atualizar(
            descricao="Descrição alterada",
            severidade=11
        )

    assert vulnerabilidade_teste.descricao == "SQL Injection"
    assert vulnerabilidade_teste.severidade == 7.1


def test_serializacao_vulnerabilidade(
    vulnerabilidade_teste
):
    dados = vulnerabilidade_teste.to_dict()

    recuperada = Vulnerabilidade.from_dict(dados)

    assert recuperada.id == 501
    assert recuperada.descricao == "SQL Injection"
    assert recuperada.categoria == "CWE-89"
    assert recuperada.severidade == 7.1
    assert recuperada.status == Tratamento.ABERTO
