from abc import ABC, abstractmethod


class EstrategiaOrdenacaoAtivos(ABC):

    @abstractmethod
    def ordenar(self, ativos):
        pass


class OrdenarPorNome(EstrategiaOrdenacaoAtivos):

    def ordenar(self, ativos):

        return sorted(
            ativos,
            key=lambda ativo: ativo.nome.lower()
        )


class OrdenarPorRiscoProprio(EstrategiaOrdenacaoAtivos):

    def ordenar(self, ativos):

        return sorted(
            ativos,
            key=self._calcular_risco,
            reverse=True
        )


    def _calcular_risco(self, ativo):

        return sum(
            vulnerabilidade.obter_severidade_efetiva()
            for vulnerabilidade
            in ativo.vulnerabilidades
        )
    
def ordenar_com_funcao(
        ativos,
        criterio,
        reverse=False
):
        
        return sorted(
            ativos,
            key=criterio,
            reverse=reverse
        )