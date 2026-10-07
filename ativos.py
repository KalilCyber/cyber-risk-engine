from abc import ABC, abstractmethod

import vulnerabilidades


# Classes que representam os ativos


class Ativo(ABC):
    def __init__(self, id, nome, responsavel, setor, vulnerabilidade):
        self.id = id
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor
        self.vulnerabilidades = vulnerabilidades
    
    @abstractmethod
    def exibir_ativo(self):
        print(f"ID {self.id}")
        print(f"nome {self.nome}")
        print(f"responsavel {self.responsavel}")
        print(f"setor {self.setor}")
        print(f"vulnerabilidades {self.vulnerabilidades}")


class Notebook(Ativo):
    def __init__(self, id, nome, responsavel, setor, vulnerabilidades, processador):
        super().__init__(id, nome, responsavel, setor, vulnerabilidades)
        self.processador = processador
    def exibir_ativo(self):
        super().exibir_ativo()
        print(f"Processador: {self.processador}") 

class Servidor(Ativo):
    def __init__(self, id, nome, responsavel, setor, vulnerabilidades, servico):
        super().__init__(id, nome, responsavel, setor, vulnerabilidades)
        self.servico = servico
    def exibir_ativo(self):
        super().exibir_ativo()
        print(f"servico {self.servico}")
        

class Roteador(Ativo):
    def __init__(self, id, nome, responsavel, setor, vulnerabilidades, endereco_ip):
        super().__init__(id, nome, responsavel, setor, vulnerabilidades)
        self.endereco_ip = endereco_ip
    def exibir_ativo(self):
        super().exibir_ativo()
        print(f"endereco_ip {self.endereco_ip}")



