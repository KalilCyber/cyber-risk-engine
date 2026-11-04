"""Rotas adicionais para a interface web do Cyber Risk Engine.

Integre no app com:
    from api.rotas_web import criar_router
    app.include_router(criar_router(lambda: inventario, lambda: servico_cve))

Mantém as regras no domínio/inventário, sem criar uma segunda base de dados.
"""
from __future__ import annotations

import copy
import math
import threading
from collections.abc import Callable
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator

from dominio.enums import NivelDependencia, Tratamento
from dominio.vulnerabilidades import Vulnerabilidade
from servicos.modelo_risco import ModeloRisco
from servicos.servico_cve import ServicoCVE


_lock = threading.RLock()


def _texto(valor: str, campo: str) -> str:
    valor = valor.strip()
    if not valor or not any(caractere.isalpha() for caractere in valor):
        raise ValueError(f"{campo} deve conter texto válido.")
    return valor


class AtualizacaoAtivo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str | None = None
    responsavel: str | None = None
    setor: str | None = None
    atributo_especifico: str | None = None

    @field_validator("nome", "responsavel", "setor", "atributo_especifico")
    @classmethod
    def validar_campo(cls, valor, info):
        return _texto(valor, info.field_name) if valor is not None else valor


class NovaVulnerabilidade(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: int = Field(gt=0)
    descricao: str = Field(min_length=1)
    categoria: str = Field(min_length=1)
    severidade: float = Field(ge=0, le=10, allow_inf_nan=False)
    status: Literal["ABERTO", "EM_TRATAMENTO", "CORRIGIDA", "ACEITA"] = "ABERTO"
    cve_id: str | None = None
    cwe_id: str | None = None
    cvss_vector: str | None = None
    cvss_version: str | None = None

    @field_validator("descricao", "categoria")
    @classmethod
    def validar_texto(cls, valor, info):
        return _texto(valor, info.field_name)

    @field_validator("cve_id", "cwe_id", "cvss_vector", "cvss_version")
    @classmethod
    def limpar_opcionais(cls, valor):
        return valor.strip() or None if valor is not None else None


class AtualizacaoVulnerabilidade(BaseModel):
    model_config = ConfigDict(extra="forbid")
    descricao: str | None = None
    categoria: str | None = None
    severidade: float | None = Field(default=None, ge=0, le=10, allow_inf_nan=False)
    status: Literal["ABERTO", "EM_TRATAMENTO", "CORRIGIDA", "ACEITA"] | None = None

    @field_validator("descricao", "categoria")
    @classmethod
    def validar_texto(cls, valor, info):
        return _texto(valor, info.field_name) if valor is not None else None


class NovaDependencia(BaseModel):
    model_config = ConfigDict(extra="forbid")
    origem_id: int = Field(gt=0)
    nivel: Literal["MUITO_BAIXA", "BAIXA", "MODERADA", "ALTA", "MUITO_ALTA"]


def criar_router(obter_inventario: Callable, obter_servico_cve: Callable | None = None) -> APIRouter:
    """A função de acesso ao inventário preserva o monkeypatch dos testes existentes."""
    router = APIRouter(tags=["Interface web"])

    def inv():
        return obter_inventario()

    def ativo_ou_404(id_ativo: int):
        ativo = inv().buscar_por_id(id_ativo)
        if ativo is None:
            raise HTTPException(404, "Ativo não encontrado.")
        return ativo

    def vuln_ou_404(id_ativo: int, id_vuln: int):
        ativo = ativo_ou_404(id_ativo)
        vul = next((v for v in ativo.vulnerabilidades if v.id == id_vuln), None)
        if vul is None:
            raise HTTPException(404, "Vulnerabilidade não encontrada neste ativo.")
        return ativo, vul

    def transacao(operacao):
        """Valida e grava; caso falhe, restaura o inventário em memória.

        Uso acadêmico de processo único; não resolve concorrência entre CLI e API
        em processos diferentes gravando no mesmo arquivo.
        """
        with _lock:
            inventario = inv()
            antes = copy.deepcopy(inventario.listar_ativos())
            try:
                retorno = operacao(inventario)
                inventario.salvar()
                return retorno
            except HTTPException:
                inventario.ativos = antes
                raise
            except (ValueError, TypeError, KeyError, AttributeError) as erro:
                inventario.ativos = antes
                raise HTTPException(status_code=422, detail=str(erro)) from erro
            except Exception:
                inventario.ativos = antes
                raise

    @router.put("/ativos/{id_ativo}")
    def atualizar_ativo(id_ativo: int, dados: AtualizacaoAtivo):
        atualizacoes = dados.model_dump(exclude_unset=True, exclude_none=True)
        if not atualizacoes:
            raise HTTPException(422, "Informe ao menos um campo para atualizar.")

        def operacao(inventario):
            if inventario.buscar_por_id(id_ativo) is None:
                raise HTTPException(404, "Ativo não encontrado.")
            ok = inventario.atualizar_ativo(id_ativo, **atualizacoes)
            if ok is False:
                raise HTTPException(404, "Ativo não encontrado.")
            return inventario.buscar_por_id(id_ativo).to_dict()

        return transacao(operacao)

    @router.delete("/ativos/{id_ativo}")
    def excluir_ativo(id_ativo: int):
        def operacao(inventario):
            if inventario.buscar_por_id(id_ativo) is None:
                raise HTTPException(404, "Ativo não encontrado.")
            inventario.remover_ativo(id_ativo)
            return {"mensagem": "Ativo removido.", "id": id_ativo}
        return transacao(operacao)

    @router.get("/ativos/{id_ativo}/vulnerabilidades")
    def listar_vulnerabilidades(id_ativo: int):
        return [v.to_dict() for v in ativo_ou_404(id_ativo).vulnerabilidades]

    @router.post("/ativos/{id_ativo}/vulnerabilidades", status_code=201)
    def cadastrar_vulnerabilidade(id_ativo: int, dados: NovaVulnerabilidade):
        def operacao(inventario):
            ativo_ou_404(id_ativo)
            vulnerabilidade = Vulnerabilidade(
                dados.id, dados.descricao, dados.categoria, dados.severidade,
                Tratamento[dados.status], dados.cve_id, dados.cwe_id,
                dados.cvss_vector, dados.cvss_version
            )
            if inventario.associar_vulnerabilidade(id_ativo, vulnerabilidade) is False:
                raise HTTPException(404, "Ativo não encontrado.")
            return vulnerabilidade.to_dict()
        return transacao(operacao)

    @router.patch("/ativos/{id_ativo}/vulnerabilidades/{id_vuln}")
    def atualizar_vulnerabilidade(id_ativo: int, id_vuln: int, dados: AtualizacaoVulnerabilidade):
        alteracoes = dados.model_dump(exclude_unset=True, exclude_none=True)
        if not alteracoes:
            raise HTTPException(422, "Informe ao menos um campo para atualizar.")
        if "status" in alteracoes:
            alteracoes["status"] = Tratamento[alteracoes["status"]]

        def operacao(inventario):
            _, vuln = vuln_ou_404(id_ativo, id_vuln)
            if "severidade" in alteracoes and vuln.cve_id:
                for outro_ativo in inventario.listar_ativos():
                    for outra in outro_ativo.vulnerabilidades:
                        if (outra is not vuln and outra.cve_id and
                            outra.cve_id.upper() == vuln.cve_id.upper() and
                            outra.severidade != alteracoes["severidade"]):
                            raise HTTPException(409, "CVSS inconsistente com outro registro do mesmo CVE.")
            resultado = inventario.atualizar_vulnerabilidade(id_ativo, id_vuln, **alteracoes)
            if resultado is False:
                raise HTTPException(404, "Vulnerabilidade não encontrada.")
            return vuln.to_dict()
        return transacao(operacao)

    @router.delete("/ativos/{id_ativo}/vulnerabilidades/{id_vuln}")
    def remover_vulnerabilidade(id_ativo: int, id_vuln: int):
        def operacao(inventario):
            ativo, vulnerabilidade = vuln_ou_404(id_ativo, id_vuln)
            ativo.vulnerabilidades.remove(vulnerabilidade)
            return {"mensagem": "Vulnerabilidade removida.", "id": id_vuln}
        return transacao(operacao)

    @router.get("/ativos/{id_ativo}/dependencias")
    def listar_dependencias(id_ativo: int):
        return ativo_ou_404(id_ativo).dependencias

    @router.post("/ativos/{id_ativo}/dependencias", status_code=201)
    def cadastrar_dependencia(id_ativo: int, dados: NovaDependencia):
        def operacao(inventario):
            ativo_ou_404(id_ativo)
            inventario.cadastrar_dependencia(id_ativo, dados.origem_id, NivelDependencia[dados.nivel])
            return ativo_ou_404(id_ativo).dependencias
        return transacao(operacao)

    @router.delete("/ativos/{id_ativo}/dependencias/{origem_id}")
    def remover_dependencia(id_ativo: int, origem_id: int):
        def operacao(inventario):
            ativo = ativo_ou_404(id_ativo)
            anterior = len(ativo.dependencias)
            ativo.dependencias = [d for d in ativo.dependencias if d["id_ativo_origem"] != origem_id]
            if len(ativo.dependencias) == anterior:
                raise HTTPException(404, "Dependência não encontrada.")
            return {"mensagem": "Dependência removida."}
        return transacao(operacao)

    @router.get("/risco")
    def analisar_risco():
        modelo = ModeloRisco(inv())
        try:
            x = modelo.calcular_risco_efetivo()
        except (ValueError, ArithmeticError) as erro:
            raise HTTPException(422, detail=str(erro)) from erro
        riscos = []
        for i, ativo in enumerate(modelo.ativos):
            riscos.append({
                "id": ativo.id, "nome": ativo.nome, "tipo": ativo.tipo,
                "risco_proprio": float(modelo.vetor_b[i]),
                "risco_efetivo": float(x[i])
            })
        condicao = modelo.numero_condicao
        return {
            "ativos": riscos,
            "numero_condicao": float(condicao) if condicao is not None and math.isfinite(float(condicao)) else None,
            "matrizes": {
                "M": modelo.matriz_m.tolist(),
                "v": modelo.vetor_v.tolist(),
                "b": modelo.vetor_b.tolist(),
                "A": modelo.matriz_a.tolist(),
                "I_menos_A": modelo.matriz_sistema.tolist(),
                "x": modelo.vetor_x.tolist()
            }
        }

    @router.get("/cves")
    def consultar_cves(termo: str = Query(min_length=2, max_length=120)):
        servico = obter_servico_cve() if obter_servico_cve else ServicoCVE()
        try:
            return servico.pesquisar_por_nome(termo, limite=8)
        except ConnectionError as erro:
            raise HTTPException(502, detail=str(erro)) from erro
        except Exception as erro:
            # Não divulga detalhes internos de falhas inesperadas.
            raise HTTPException(502, detail="Não foi possível consultar a NVD neste momento.") from erro

    return router
