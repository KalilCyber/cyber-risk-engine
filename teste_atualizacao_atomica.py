"""Execute na raiz do projeto: python teste_atualizacao_atomica.py"""
from dominio.ativos import Notebook, Servidor, Roteador, AplicacaoWeb
from servicos.inventario import Inventario


def verificar(ativo, alteracao_invalida, alteracao_valida, campo):
    inventario = Inventario([ativo])
    original = ativo.to_dict()
    try:
        inventario.atualizar_ativo(
            ativo.id,
            nome="Nome Alterado",
            atributo_especifico=alteracao_invalida
        )
    except ValueError as erro:
        print(f"OK - {ativo.tipo}: rejeitou valor inválido ({erro})")
    else:
        raise AssertionError(f"{ativo.tipo}: aceitou valor inválido")
    assert ativo.to_dict() == original, "O objeto foi alterado parcialmente!"

    assert inventario.atualizar_ativo(
        ativo.id, nome="Nome Alterado", atributo_especifico=alteracao_valida
    ) is True
    assert ativo.nome == "Nome Alterado"
    assert getattr(ativo, campo) == alteracao_valida
    assert inventario.atualizar_ativo(99999, nome="Outro") is False
    print(f"OK - {ativo.tipo}: atualização válida concluída")


verificar(Notebook(1, "Notebook Teste", "Aline", "TI", [], "Intel Core i5"),
          "-2", "AMD Ryzen 5", "processador")
verificar(Servidor(2, "Servidor Teste", "Aline", "TI", [], "Banco de Dados"),
          "-2", "Servidor Web", "servico")
verificar(Roteador(3, "Roteador Teste", "Aline", "TI", [], "192.168.0.1"),
          "-2", "192.168.0.2", "endereco_ip")
verificar(AplicacaoWeb(4, "Aplicacao Teste", "Aline", "TI", [], "https://exemplo.com"),
          "-2", "https://sistema.exemplo.com", "url")

print("Todos os testes de atualização atômica passaram.")
