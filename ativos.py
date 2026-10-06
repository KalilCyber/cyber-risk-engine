# Classes que representam os ativos

class Ativo:
    def __init__(self, id, nome, responsavel, setor, vulnerabilidade):
        self.id = id
        self.nome = nome
        self.responsavel = responsavel
        self.setor = setor
        self.vulnerabilidade = vulnerabilidade
    

    def exibir_ativo(self):
        print(f"ID {self.id}")
        print(f"nome {self.nome}")
        print(f"responsavel {self.responsavel}")
        print(f"setor {self.setor}")
        print(f"vulnerabilidade {self.vulnerabilidade}")


class Notebook(Ativo):
    def __init__(self, id, nome, responsavel, setor, vulnerabilidade, processador):
        super().__init__(id, nome, responsavel, setor, vulnerabilidade)
        self.processador = processador
    def exibir_ativo(self):
        print(f"processador {self.processador}")
        return super().exibir_ativo()

class Servidor(Ativo):
    def __init__(self, id, nome, responsavel, setor, vulnerabilidade, servico):
        super().__init__(id, nome, responsavel, setor, vulnerabilidade)
        self.servico = servico
    def exibir_ativo(self):
        print(f"servico {self.servico}")
        return super().exibir_ativo()

class Roteador(Ativo):
    def __init__(self, id, nome, responsavel, setor, vulnerabilidade, endereco_ip):
        super().__init__(id, nome, responsavel, setor, vulnerabilidade)
        self.endereco_ip = endereco_ip
    def exibir_ativo(self):
        print(f"endereco_ip {self.endereco_ip}")
        return super().exibir_ativo()



