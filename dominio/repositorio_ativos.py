from abc import ABC, abstractmethod


class RepositorioAtivos(ABC):

    @abstractmethod
    def carregar(self):
        pass


    @abstractmethod
    def salvar(self, ativos):
        pass