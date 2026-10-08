from ativos import Notebook, Servidor, Roteador

from vulnerabilidades import Vulnerabilidade

from persistencia import Persistencia


# ============================================================
# CRIAÇÃO DAS VULNERABILIDADES
# ============================================================

vulnerabilidade1 = Vulnerabilidade(
    1,
    "Senha fraca",
    "Autenticação",
    6.5,
    "ABERTA"
)


vulnerabilidade2 = Vulnerabilidade(
    2,
    "Sistema operacional desatualizado",
    "Software desatualizado",
    8.0,
    "ABERTA"
)


vulnerabilidade3 = Vulnerabilidade(
    3,
    "Serviço SSH exposto",
    "Serviço de acesso remoto",
    9.0,
    "EM_TRATAMENTO"
)


# ============================================================
# CRIAÇÃO DOS ATIVOS
# ============================================================

notebook1 = Notebook(
    1,
    "Notebook K",
    "Kalil",
    "Cibersegurança",
    [],
    "Intel Core i5"
)


notebook2 = Notebook(
    2,
    "Notebook Dell",
    "Kalil",
    "Cibersegurança",
    [],
    "Intel Core i7"
)


servidor1 = Servidor(
    3,
    "Servidor Principal",
    "Kalil",
    "Cibersegurança",
    [],
    "Servidor Web"
)


roteador1 = Roteador(
    4,
    "Roteador Principal",
    "Kalil",
    "Infraestrutura",
    [],
    "192.168.0.1"
)


# ============================================================
# ASSOCIAÇÃO DAS VULNERABILIDADES
# ============================================================

notebook1.adicionar_vulnerabilidade(
    vulnerabilidade1
)

notebook1.adicionar_vulnerabilidade(
    vulnerabilidade2
)


notebook2.adicionar_vulnerabilidade(
    vulnerabilidade2
)


servidor1.adicionar_vulnerabilidade(
    vulnerabilidade2
)

servidor1.adicionar_vulnerabilidade(
    vulnerabilidade3
)


roteador1.adicionar_vulnerabilidade(
    vulnerabilidade1
)


# ============================================================
# LISTA DE ATIVOS
# ============================================================

ativos = [
    notebook1,
    notebook2,
    servidor1,
    roteador1
]


# ============================================================
# EXIBIÇÃO POLIMÓRFICA
# ============================================================

print(
    "\n--- ATIVOS CADASTRADOS ---"
)


for ativo in ativos:

    ativo.exibir_ativo()

    print("-" * 50)


# ============================================================
# PERSISTÊNCIA
# ============================================================

persistencia = Persistencia()


persistencia.salvar(
    ativos
)


# ============================================================
# TESTE DE RECARGA
# ============================================================

print(
    "\n--- ATIVOS CARREGADOS DO JSON ---"
)


ativos_carregados = (
    persistencia.carregar()
)


for ativo in ativos_carregados:

    ativo.exibir_ativo()

    print("-" * 50)