class Inventario:
    
    def __init__(self, ativos=None):

        if ativos is None:
            self.ativos = []
        else:
          self.ativos = ativos
    
    def cadastrar_ativo(self, ativo):

        for ativo_existente in self.ativos:

            if ativo_existente.id == ativo.id:
                raise ValueError(f"Já existe um ativo com o ID {ativo.id}.")
        
        self.ativos.append(ativo)
    
    def listar_ativos(self):
        
        return self.ativos.copy()
    
    def buscar_por_id(self, id_ativo):

        for ativo in self.ativos:

            if ativo.id == id_ativo:
                return ativo
        
        return None
    
    def buscar_por_nome(self, nome):

        resultados = []

        for ativo in self.ativos:

            if nome.lower() in ativo.nome.lower():
                resultados.append(ativo)
        
        return resultados
