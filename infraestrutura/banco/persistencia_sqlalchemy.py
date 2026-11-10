from math import isclose, isfinite
from dominio.enums import NivelDependencia

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from dominio.repositorio_ativos import RepositorioAtivos
from infraestrutura.banco.sessao import criar_fabrica_sessoes

from infraestrutura.banco.modelos import (
    AtivoDB,
    VulnerabilidadeDB,
    AtivoVulnerabilidadeDB,
    DependenciaDB,
)

from infraestrutura.banco.conversores import (
    ativo_para_modelo,
    modelo_para_ativo,
    vulnerabilidade_para_modelo,
)


class PersistenciaSQLAlchemy(RepositorioAtivos):

    def __init__(self, engine):
        self._fabrica_sessoes = criar_fabrica_sessoes(engine)

   
    def carregar(self):
        """Recupera ativos, vulnerabilidades e dependências."""

        with self._fabrica_sessoes() as sessao:

            consulta = (
                select(AtivoDB)
                .options(
                    # Carrega vulnerabilidades associadas
                    selectinload(
                        AtivoDB.associacoes_vulnerabilidades
                    ).selectinload(
                        AtivoVulnerabilidadeDB.vulnerabilidade
                    ),

                    # Carrega as dependências do ativo
                    selectinload(
                        AtivoDB.dependencias_como_destino
                    )
                )
                .order_by(AtivoDB.id)
            )

            modelos = sessao.scalars(consulta).all()

            return [
                modelo_para_ativo(modelo)
                for modelo in modelos
            ]

   
    def salvar(self, ativos):
        """Salva o inventário completo em uma transação."""

        ativos = list(ativos)

        modelos_por_id = {}
        catalogo_vulnerabilidades = {}
        associacoes = []
        dependencias = []

        campos_tecnicos = (
            "descricao",
            "categoria",
            "severidade",
            "cve_id",
            "cwe_id",
            "cvss_vector",
            "cvss_version",
        )

        # 1. Prepara os ativos e verifica IDs duplicados.
        for ativo in ativos:

            if ativo.id in modelos_por_id:
                raise ValueError(
                    f"Ativo duplicado: {ativo.id}."
                )

            modelo = ativo_para_modelo(
                ativo,
                permitir_vulnerabilidades=True,
                permitir_dependencias=True
            )

            modelos_por_id[ativo.id] = modelo

        # 2. Prepara vulnerabilidades e associações.
        for ativo in ativos:

            modelo_ativo = modelos_por_id[ativo.id]
            ids_associados = set()

            for vulnerabilidade in ativo.vulnerabilidades:

                if vulnerabilidade.id in ids_associados:
                    raise ValueError(
                        "Vulnerabilidade duplicada no ativo."
                    )

                ids_associados.add(vulnerabilidade.id)

                novo_modelo = vulnerabilidade_para_modelo(
                    vulnerabilidade
                )

                existente = catalogo_vulnerabilidades.get(
                    vulnerabilidade.id
                )

                if existente is None:
                    catalogo_vulnerabilidades[
                        vulnerabilidade.id
                    ] = novo_modelo

                    modelo_vulnerabilidade = novo_modelo

                else:
                    if any(
                        getattr(existente, campo)
                        != getattr(novo_modelo, campo)
                        for campo in campos_tecnicos
                    ):
                        raise ValueError(
                            "Dados técnicos inconsistentes "
                            f"para a vulnerabilidade "
                            f"{vulnerabilidade.id}."
                        )

                    modelo_vulnerabilidade = existente

                associacoes.append(
                    AtivoVulnerabilidadeDB(
                        ativo=modelo_ativo,
                        vulnerabilidade=modelo_vulnerabilidade,
                        status=vulnerabilidade.status.name
                    )
                )

        # 3. Valida e prepara as dependências.
        for ativo in ativos:

            ids_origem = set()
            soma_pesos = 0.0

            for dependencia in ativo.dependencias:

                origem_id = dependencia["id_ativo_origem"]

                if origem_id not in modelos_por_id:
                    raise ValueError(
                        f"Ativo de origem {origem_id} "
                        "não existe no inventário."
                    )

                if origem_id == ativo.id:
                    raise ValueError(
                        "Um ativo não pode depender de si mesmo."
                    )

                if origem_id in ids_origem:
                    raise ValueError(
                        "Dependência duplicada para o ativo."
                    )

                ids_origem.add(origem_id)

                peso = float(dependencia["peso"])

                if not isfinite(peso) or not 0 <= peso < 1:
                    raise ValueError(
                        "Peso de dependência inválido."
                    )

                nivel = dependencia.get("nivel")
                valor_nist = dependencia.get("valor_nist")

                # Valida a coerência com a escala do domínio.
                if nivel is not None:

                    try:
                        nivel_enum = NivelDependencia[nivel]
                    except (KeyError, TypeError) as erro:
                        raise ValueError(
                            "Nível de dependência inválido."
                        ) from erro

                    if (
                        valor_nist is not None
                        and valor_nist != nivel_enum.value
                    ):
                        raise ValueError(
                            "Valor NIST incompatível com o nível."
                        )

                    if not isclose(
                        peso,
                        nivel_enum.value / 20,
                        rel_tol=0,
                        abs_tol=1e-9
                    ):
                        raise ValueError(
                            "Peso incompatível com o nível."
                        )

                elif valor_nist is not None:

                    if (
                        valor_nist not in
                        [n.value for n in NivelDependencia]
                        or not isclose(
                            peso,
                            valor_nist / 20,
                            rel_tol=0,
                            abs_tol=1e-9
                        )
                    ):
                        raise ValueError(
                            "Valor NIST e peso incompatíveis."
                        )

                soma_pesos += peso

                if soma_pesos >= 1:
                    raise ValueError(
                        "A soma dos pesos das dependências "
                        "deve permanecer menor que 1."
                    )

                dependencias.append(
                    DependenciaDB(
                        ativo_destino=modelos_por_id[ativo.id],
                        ativo_origem=modelos_por_id[origem_id],
                        nivel=nivel,
                        valor_nist=valor_nist,
                        peso=peso
                    )
                )

        # 4. Executa a substituição dentro de uma transação.
        with self._fabrica_sessoes.begin() as sessao:

            # Apaga primeiro as tabelas associativas.
            sessao.execute(delete(DependenciaDB))
            sessao.execute(delete(AtivoVulnerabilidadeDB))

            sessao.execute(delete(VulnerabilidadeDB))
            sessao.execute(delete(AtivoDB))

            # Insere a nova fotografia do inventário.
            sessao.add_all(list(modelos_por_id.values()))

            sessao.add_all(
                list(catalogo_vulnerabilidades.values())
            )

            sessao.add_all(associacoes)
            sessao.add_all(dependencias)

