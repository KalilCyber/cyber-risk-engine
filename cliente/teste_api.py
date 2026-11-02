
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

URL_BASE = "http://127.0.0.1:8000"


def requisicao(metodo, rota, dados=None):
    corpo = None

    if dados is not None:
        corpo = json.dumps(dados).encode("utf-8")

    pedido = Request(
        URL_BASE + rota,
        data=corpo,
        headers={"Content-Type": "application/json"},
        method=metodo
    )

    try:
        with urlopen(pedido, timeout=10) as resposta:
            return (
                resposta.status,
                json.load(resposta)
            )

    except HTTPError as erro:
        return (
            erro.code,
            json.load(erro)
        )


def testar_api():
    print("\n--- TESTE DE HEALTH ---")

    status, resposta = requisicao("GET", "/health")
    assert status == 200
    assert resposta["status"] == "ok"
    print("OK - Serviço HTTP funcionando")

    print("\n--- TESTE DE LISTAGEM ---")

    status, ativos = requisicao("GET", "/ativos")
    assert status == 200
    assert isinstance(ativos, list)
    print(f"OK - {len(ativos)} ativos encontrados")

    print("\n--- TESTE DE CONSULTA ---")

    status, ativo = requisicao("GET", "/ativos/7")
    assert status == 200
    assert ativo["id"] == 7
    print("OK - Notebook Acer Nitro consultado")

    print("\n--- TESTE DE ATIVO INEXISTENTE ---")

    status, _ = requisicao("GET", "/ativos/999999")
    assert status == 404
    print("OK - Ativo inexistente retorna 404")

    print("\n--- TESTE DE CADASTRO ---")

    novo_ativo = {
        "id": 9001,
        "nome": "Notebook Teste API",
        "responsavel": "Aline",
        "setor": "Cibersegurança",
        "tipo": "Notebook",
        "processador": "Intel Core i5"
    }

    status, resposta = requisicao(
        "POST", "/ativos", novo_ativo
    )

    assert status == 201, resposta
    print("OK - Ativo cadastrado via HTTP")

    status, resposta = requisicao(
        "GET", "/ativos/9001"
    )

    assert status == 200
    assert resposta["nome"] == "Notebook Teste API"
    print("OK - Cadastro disponível para consulta")

    print("\n--- TESTE DE ID DUPLICADO ---")

    status, _ = requisicao(
        "POST", "/ativos", novo_ativo
    )

    assert status == 409
    print("OK - ID duplicado rejeitado")

    print("\n--- TESTE DE ENTRADA INVÁLIDA ---")

    invalido = novo_ativo.copy()
    invalido["id"] = 9002
    invalido["processador"] = "-2"

    status, _ = requisicao(
        "POST", "/ativos", invalido
    )

    assert status == 422
    print("OK - Processador inválido rejeitado")

    print("\nTODOS OS TESTES HTTP PASSARAM!")


if __name__ == "__main__":
    testar_api()
