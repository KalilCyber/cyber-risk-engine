"""Diário de eventos da API web do Cyber Risk Engine.

Registra diferenças de estado somente depois de requisições HTTP bem-sucedidas.
Uso acadêmico/local, não é trilha de auditoria imutável nem monitor 24h.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from fastapi import APIRouter, FastAPI, Query, Request

log = logging.getLogger(__name__)
_lock = threading.RLock()


def caminho_diario() -> Path:
    """Arquivo separado do inventário; variável explícita tem prioridade."""
    especifico = os.environ.get("CYBER_RISK_JOURNAL")
    if especifico:
        return Path(especifico)
    dados = Path(os.environ.get("CYBER_RISK_DATA", "ativos.json"))
    return dados.with_name(f"{dados.stem}_diario.jsonl")


def _nome_status(status: object) -> str:
    return getattr(status, "name", str(status))


def _fotografia(inventario) -> dict:
    """Snapshot sem referências mutáveis, em formato mínimo para comparação."""
    ativos = {}
    vulns = {}
    deps = {}
    for ativo in inventario.listar_ativos():
        ident = int(ativo.id)
        ativos[ident] = str(ativo.nome)
        for v in getattr(ativo, "vulnerabilidades", []):
            chave = (ident, int(v.id))
            vulns[chave] = {
                "ativo_id": ident,
                "ativo_nome": str(ativo.nome),
                "vulnerabilidade_id": int(v.id),
                "cve_id": str(v.cve_id) if getattr(v, "cve_id", None) else None,
                "status": _nome_status(v.status),
            }
        for d in getattr(ativo, "dependencias", []):
            origem = int(d["id_ativo_origem"])
            deps[(ident, origem)] = {
                "ativo_id": ident,
                "ativo_nome": str(ativo.nome),
                "origem_id": origem,
            }
    return {"ativos": ativos, "vulns": vulns, "deps": deps}


def _diferencas(antes: dict, depois: dict) -> list[dict]:
    eventos = []
    for ident, nome in depois["ativos"].items():
        if ident not in antes["ativos"]:
            eventos.append({"tipo": "ativo_cadastrado", "ativo_id": ident, "ativo_nome": nome})
        elif antes["ativos"][ident] != nome:
            eventos.append({"tipo": "ativo_atualizado", "ativo_id": ident, "ativo_nome": nome})
    for ident, nome in antes["ativos"].items():
        if ident not in depois["ativos"]:
            eventos.append({"tipo": "ativo_removido", "ativo_id": ident, "ativo_nome": nome})

    for chave, v in depois["vulns"].items():
        anterior = antes["vulns"].get(chave)
        if anterior is None:
            eventos.append({"tipo": "vulnerabilidade_associada", **v, "status_novo": v["status"]})
        elif anterior["status"] != v["status"]:
            eventos.append({"tipo": "tratamento_atualizado", **{k: val for k, val in v.items() if k != "status"},
                            "status_anterior": anterior["status"], "status_novo": v["status"]})
    for chave, v in antes["vulns"].items():
        if chave not in depois["vulns"]:
            eventos.append({"tipo": "vulnerabilidade_removida", **v})

    for chave, d in depois["deps"].items():
        if chave not in antes["deps"]:
            eventos.append({"tipo": "dependencia_criada", **d})
    for chave, d in antes["deps"].items():
        if chave not in depois["deps"]:
            eventos.append({"tipo": "dependencia_removida", **d})
    return eventos


def registrar(eventos: list[dict]) -> None:
    """Append de entradas JSONL; um processo único, sincronizado por lock."""
    if not eventos:
        return
    path = caminho_diario()
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as arquivo:
            for evento in eventos:
                registro = {"evento_id": str(uuid.uuid4()), "hora": datetime.now(timezone.utc).isoformat(), **evento}
                arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
            arquivo.flush()
            os.fsync(arquivo.fileno())


def ler(limite: int = 200) -> dict:
    path = caminho_diario()
    if not path.exists():
        return {"eventos": [], "total": 0, "resumo": {"em_tratamento": 0, "corrigidas": 0}}
    with _lock:
        with path.open("r", encoding="utf-8") as arquivo:
            ultimos = deque(maxlen=limite)
            total = 0
            em_tratamento = 0
            corrigidas = 0
            for linha in arquivo:
                if not linha.strip():
                    continue
                item = json.loads(linha)
                total += 1
                if item.get("tipo") == "tratamento_atualizado":
                    em_tratamento += item.get("status_novo") == "EM_TRATAMENTO"
                    corrigidas += item.get("status_novo") == "CORRIGIDA"
                ultimos.append(item)
    return {"eventos": list(reversed(ultimos)), "total": total,
            "resumo": {"em_tratamento": em_tratamento, "corrigidas": corrigidas}}


def instalar_diario(app: FastAPI, obter_inventario: Callable) -> None:
    """Instale uma única vez após criar o app e o inventário, antes de iniciar o Uvicorn."""
    router = APIRouter(tags=["Diário da Caçada"])

    @router.get("/diario")
    def consultar_diario(limite: int = Query(200, ge=1, le=500)):
        return ler(limite)

    app.include_router(router)

    @app.middleware("http")
    async def registrar_operacoes(request: Request, call_next):
        observar = request.method in {"POST", "PUT", "PATCH", "DELETE"} and request.url.path.startswith("/ativos")
        if not observar:
            return await call_next(request)
        # Snapshot antes e depois da operação. Em requisições concorrentes, a
        # associação de eventos à requisição não é uma garantia auditável.
        anterior = _fotografia(obter_inventario())
        response = await call_next(request)
        if 200 <= response.status_code < 300:
            try:
                atual = _fotografia(obter_inventario())
                registrar(_diferencas(anterior, atual))
            except Exception:
                # A gravação do inventário já concluiu: nunca fingir que foi
                # desfeita por um erro posterior no diário.
                log.exception("Falha ao registrar evento no Diário da Caçada. Verifique disco/permissões.")
        return response
