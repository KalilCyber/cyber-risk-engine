from enum import Enum


class Tratamento(Enum):

    ABERTO = 1
    EM_TRATAMENTO = 2
    CORRIGIDA = 3
    ACEITA = 4

   

class NivelDependencia(Enum):

    MUITO_BAIXA = 0
    BAIXA = 2
    MODERADA = 5
    ALTA = 8
    MUITO_ALTA = 10