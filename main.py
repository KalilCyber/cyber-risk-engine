from ativos import Notebook
from persistencia import Persistencia


notebook1 = Notebook(
    1,
    "Notebook K",
    "Kalil",
    "Cibersegurança",
    "Senha Fraca",
    "8gb")


notebook2 = Notebook(
    2,
    "Notebook Dell",
    "Kalil",
    "Cibersegurança",
    "Windows desatualizado",
    "32gb")

ativos=[notebook1, notebook2]

for ativos in ativos:
    print(ativos.exibir_ativo())

Persistencia()