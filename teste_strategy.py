from infraestrutura.persistencia_json import Persistencia
from servicos.inventario import Inventario

from servicos.estrategias_ordenacao import (
    OrdenarPorNome,
    OrdenarPorRiscoProprio
)

from servicos.estrategias_ordenacao import ordenar_com_funcao


repositorio = Persistencia()

ativos = repositorio.carregar()

inventario = Inventario(
    ativos,
    repositorio
)


print(
    "\n--- ATIVOS ORDENADOS POR NOME ---"
)

ativos_por_nome = (
    inventario.listar_ativos_ordenados(
        OrdenarPorNome()
    )
)


for ativo in ativos_por_nome:

    print(
        f"{ativo.id} - {ativo.nome}"
    )


print(
    "\n--- ATIVOS ORDENADOS POR RISCO PRÓPRIO ---"
)

ativos_por_risco = (
    inventario.listar_ativos_ordenados(
        OrdenarPorRiscoProprio()
    )
)


for ativo in ativos_por_risco:

    risco = sum(
        vulnerabilidade.obter_severidade_efetiva()
        for vulnerabilidade
        in ativo.vulnerabilidades
    )

    print(
        f"{ativo.id} - "
        f"{ativo.nome} - "
        f"Risco: {risco:.2f}"
    )


print(
    "\n--- ESTRATÉGIA COM FUNÇÃO ---"
)

ativos_por_tipo = ordenar_com_funcao(
    inventario.listar_ativos(),
    criterio=lambda ativo: ativo.tipo.lower()
)


for ativo in ativos_por_tipo:

    print(
        f"{ativo.id} - "
        f"{ativo.tipo} - "
        f"{ativo.nome}"
    )