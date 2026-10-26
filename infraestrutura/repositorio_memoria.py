from dominio.repositorio_ativos import RepositorioAtivos


class RepositorioMemoria(RepositorioAtivos):

    def __init__(self, ativos=None):

        if ativos is None:
            self._ativos = []

        else:
            self._ativos = list(ativos)


    def carregar(self):

        return self._ativos.copy()


    def salvar(self, ativos):

        self._ativos = list(ativos)