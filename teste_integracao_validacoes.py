"""Testes isolados. Não altera o ativos.json do projeto."""
import tempfile
from pathlib import Path
from dominio.enums import Tratamento
from dominio.vulnerabilidades import Vulnerabilidade
from infraestrutura.persistencia_json import Persistencia


def deve_rejeitar(funcao, descricao):
    try:
        funcao()
    except ValueError:
        print(f"OK - rejeitou {descricao}")
    else:
        raise AssertionError(f"FALHA - aceitou {descricao}")


v = Vulnerabilidade(101, "SQL Injection", "CWE-89", 8.7, Tratamento.ABERTO)
deve_rejeitar(lambda: Vulnerabilidade(-2, "SQL Injection", "CWE-89", 8.7, Tratamento.ABERTO), "ID -2")
deve_rejeitar(lambda: Vulnerabilidade(1, "-2", "CWE-89", 8.7, Tratamento.ABERTO), "descrição -2")
deve_rejeitar(lambda: Vulnerabilidade(1, "SQL Injection", "-2", 8.7, Tratamento.ABERTO), "categoria -2")
deve_rejeitar(lambda: Vulnerabilidade(1, "SQL Injection", "CWE-89", -2, Tratamento.ABERTO), "severidade -2")
deve_rejeitar(lambda: v.atualizar(descricao="Alterada", severidade=-2), "atualização parcial inválida")
assert v.descricao == "SQL Injection", "A descrição foi alterada apesar do erro!"
assert Vulnerabilidade.from_dict(v.to_dict()).cve_id == v.cve_id

with tempfile.TemporaryDirectory() as pasta:
    caminho = Path(pasta) / "ativos.json"
    repo = Persistencia(str(caminho))
    assert repo.carregar() == [], "Arquivo ausente deveria retornar lista vazia"
    caminho.write_text("", encoding="utf-8")
    assert repo.carregar() == [], "Arquivo vazio deveria retornar lista vazia"
    caminho.write_text("{json quebrado", encoding="utf-8")
    deve_rejeitar(repo.carregar, "JSON corrompido")
    repo.salvar([])
    assert repo.carregar() == [], "Não foi possível salvar/carregar lista vazia"

print("Todos os testes isolados passaram. ativos.json original não foi alterado.")
