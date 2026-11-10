from dominio.vulnerabilidades import Vulnerabilidade

from infraestrutura.banco.modelos import (
    AtivoDB,
    VulnerabilidadeDB
)

from dominio.fabrica_ativos import FabricaAtivos



# Atributo específico de cada tipo de ativo
CAMPOS_ESPECIFICOS = {
    "Notebook": "processador",
    "Servidor": "servico",
    "Roteador": "endereco_ip",
    "AplicacaoWeb": "url"
}


def ativo_para_modelo(
    ativo,
    *,
    permitir_vulnerabilidades=False,
    permitir_dependencias=False
):
    """Converte os atributos básicos do ativo para ORM."""

    if ativo.dependencias and not permitir_dependencias:
        raise NotImplementedError(
            "As dependências precisam ser persistidas "
            "pelo Repository."
        )

    if ativo.vulnerabilidades and not permitir_vulnerabilidades:
        raise NotImplementedError(
            "As vulnerabilidades precisam ser persistidas "
            "pelo Repository."
        )
    
    campo = CAMPOS_ESPECIFICOS.get(ativo.tipo)

    if campo is None:
        raise ValueError(
            f"Tipo de ativo inválido: {ativo.tipo}"
        )

    return AtivoDB(
        id=ativo.id,
        nome=ativo.nome,
        responsavel=ativo.responsavel,
        setor=ativo.setor,
        tipo=ativo.tipo,
        **{campo: getattr(ativo, campo)}
    )


def modelo_para_ativo(modelo):
    """Reconstrói um ativo do domínio a partir do ORM."""

    campo = CAMPOS_ESPECIFICOS.get(modelo.tipo)

    if campo is None:
        raise ValueError(
            f"Tipo de ativo inválido: {modelo.tipo}"
        )

    # Reconstrução das vulnerabilidades
    vulnerabilidades = [
        associacao_para_vulnerabilidade(associacao)
        for associacao in sorted(
            modelo.associacoes_vulnerabilidades,
            key=lambda item: item.vulnerabilidade_id
        )
    ]

    # Reconstrução do ativo pela Factory
    ativo = FabricaAtivos.criar(
        modelo.tipo,
        modelo.id,
        modelo.nome,
        modelo.responsavel,
        modelo.setor,
        vulnerabilidades,
        **{campo: getattr(modelo, campo)}
    )

    # Reconstrução das dependências
    ativo.dependencias = [
        {
            "id_ativo_origem": dependencia.ativo_origem_id,
            "nivel": dependencia.nivel,
            "valor_nist": dependencia.valor_nist,
            "peso": dependencia.peso
        }
        for dependencia in sorted(
            modelo.dependencias_como_destino,
            key=lambda item: item.ativo_origem_id
        )
    ]

    return ativo

def vulnerabilidade_para_modelo(vulnerabilidade):
    """Converte dados técnicos de vulnerabilidade para ORM."""

    return VulnerabilidadeDB(
        id=vulnerabilidade.id,
        descricao=vulnerabilidade.descricao,
        categoria=vulnerabilidade.categoria,
        severidade=vulnerabilidade.severidade,
        cve_id=vulnerabilidade.cve_id,
        cwe_id=vulnerabilidade.cwe_id,
        cvss_vector=vulnerabilidade.cvss_vector,
        cvss_version=vulnerabilidade.cvss_version
    )


def associacao_para_vulnerabilidade(associacao):
    """Reconstrói uma vulnerabilidade com seu tratamento."""

    modelo = associacao.vulnerabilidade

    if modelo is None:
        raise ValueError(
            "Associação sem vulnerabilidade cadastrada."
        )

    return Vulnerabilidade(
        id=modelo.id,
        descricao=modelo.descricao,
        categoria=modelo.categoria,
        severidade=modelo.severidade,
        status=associacao.status,
        cve_id=modelo.cve_id,
        cwe_id=modelo.cwe_id,
        cvss_vector=modelo.cvss_vector,
        cvss_version=modelo.cvss_version
    )
