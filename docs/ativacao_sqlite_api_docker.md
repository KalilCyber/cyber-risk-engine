# Ativação segura do SQLite — Cyber Risk Engine

## 1. Convenção de variáveis

| Variável | Finalidade | Valor padrão |
| --- | --- | --- |
| `CYBER_RISK_STORAGE` | Repositório utilizado pela API: `json` ou `sqlite` | `json` |
| `CYBER_RISK_DATA` | Caminho do inventário JSON (modo JSON) | `ativos.json` na raiz |
| `CYBER_RISK_DB` | Caminho do banco SQLite (modo SQL) | `cyber_risk.db` na raiz |
| `CYBER_RISK_JOURNAL` | Arquivo JSONL do Diário da Caçada | definido pelo módulo do Diário |

A inicialização da API **não executa migração nem cria banco vazio automaticamente**. `CYBER_RISK_STORAGE=sqlite` exige um banco existente com revisão Alembic compatível.

## 2. Alteração em `api/app.py`

**Mantenha todas as rotas, imports de `instalar_diario`, `criar_router`, `StaticFiles` etc.** Adicione o import:

```python
from infraestrutura.seletor_repositorio import criar_repositorio_configurado
```

Localize o trecho que define a raiz e instancia o repositório JSON, similar a:

```python
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_DADOS = Path(os.getenv("CYBER_RISK_DATA", str(RAIZ_PROJETO / "ativos.json")))
repositorio = Persistencia(str(CAMINHO_DADOS))
ativos_carregados = repositorio.carregar()
```

Troque **apenas esse trecho** por:

```python
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
repositorio = criar_repositorio_configurado(RAIZ_PROJETO)
ativos_carregados = repositorio.carregar()
```

Preserve `inventario = Inventario(ativos_carregados, repositorio)` e todo o resto.

## 3. Verificação e execução local no Windows

Dentro de `feature/banco-dados` com `.venv` ativa:

```powershell
python -m pytest -q
python -m scripts.migrar_json_para_sqlite --help
```

Para criar uma cópia persistente **sem sobrescrever um banco pré-existente**:

```powershell
python -m scripts.migrar_json_para_sqlite
Get-ChildItem .\dados_sql\*.db | Sort-Object LastWriteTime -Descending | Select-Object FullName,Length
```

Confira o caminho real impresso. Em seguida, no **mesmo terminal**:

```powershell
$env:CYBER_RISK_STORAGE = "sqlite"
$env:CYBER_RISK_DB = (Get-ChildItem .\dados_sql\*.db | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
$env:CYBER_RISK_JOURNAL = (Join-Path (Get-Location) "ativos_diario.jsonl")
python -m uvicorn api.app:app --host 127.0.0.1 --port 8001
```

Teste `http://127.0.0.1:8001/health`, `http://127.0.0.1:8001/ativos` e `http://127.0.0.1:8001/ui/`.

**Atenção:** fazer cadastros em SQLite altera esse banco SQL. Após isso, trocar para JSON fará aparecer o estado anterior do JSON; não existe sincronização bidirecional automática. Evite gravar em ambos sem uma política explícita de migração.

Para encerrar o servidor: `Ctrl+C`. Para voltar ao JSON **em uma nova inicialização**:

```powershell
Remove-Item Env:\CYBER_RISK_STORAGE -ErrorAction SilentlyContinue
Remove-Item Env:\CYBER_RISK_DB -ErrorAction SilentlyContinue
Remove-Item Env:\CYBER_RISK_JOURNAL -ErrorAction SilentlyContinue
```

## 4. Dockerfile — requisitos

Preserve o restante do seu `dockerfile`. Garanta que estas entradas sejam copiadas **antes do CMD**:

```dockerfile
COPY infraestrutura/ ./infraestrutura/
COPY scripts/ ./scripts/
COPY alembic/ ./alembic/
COPY alembic.ini .
```

E que `requirements.txt` instale `SQLAlchemy` e `alembic`, além das outras dependências existentes. Já há `COPY api/`, `dominio/`, `frontend/`, `servicos/` etc. na sua estrutura.

O `dockerfile` não deve incluir `ativos.json`, banco real `.db`, logs `.jsonl` ou backups.

## 5. Docker Compose — alterações pontuais

Mantenha o serviço `api`, a porta de loopback, o `healthcheck` e o volume `dados_api:/dados` como já estão. Acrescente ao bloco `environment`:

```yaml
      CYBER_RISK_STORAGE: ${CYBER_RISK_STORAGE:-json}
      CYBER_RISK_DB: /dados/cyber_risk.db
```

Preserve também:

```yaml
      CYBER_RISK_DATA: /dados/ativos.json
      CYBER_RISK_JOURNAL: /dados/ativos_diario.jsonl
```

No `.gitignore`, confirme que `dados_sql/`, `*.db`, `*.db-*`, `.env` e backups locais estão ignorados.

No `.dockerignore`, acrescente (se ainda não existirem):

```dockerignore
*.db
*.db-*
dados_sql/
backups_cyber_risk_engine/
**/*.jsonl
```

### Fluxo seguro para um volume Docker já contendo `/dados/ativos.json`

1. Antes de migrar, confira se o serviço atualmente usa o JSON e se os dados estão íntegros:

```powershell
docker compose config
docker compose ps
docker compose run --rm --no-deps --entrypoint python api -c "from pathlib import Path; print('JSON no volume:', Path('/dados/ativos.json').is_file())"
```

Se o volume não tiver `/dados/ativos.json`, **não migre um banco vazio**. Verifique primeiro de onde virão os dados.

2. Pare as gravações antes de copiar o JSON, e crie também um backup **fora do volume Docker**, no PC (pois remover o volume apagaria os backups guardados dentro dele):

```powershell
docker compose stop api
$cid = docker compose ps -a -q api
$backupHost = "..\ativos_volume_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
docker cp "${cid}:/dados/ativos.json" $backupHost
Test-Path $backupHost
docker compose build
```

3. Migre **dentro do volume nomeado** (não da camada descartável da imagem):

```powershell
docker compose run --rm --no-deps --entrypoint python api -m scripts.migrar_json_para_sqlite --origem /dados/ativos.json --destino /dados/cyber_risk.db --backup-dir /dados/backups
```

O comando falhará se `/dados/cyber_risk.db` já existir; não o apague para forçar outra migração sem backup e reconciliação.

4. Escolha a opção SQLite persistente no arquivo `.env` **local, não versionado** (adicione a linha, não substitua outras configurações existentes):

```dotenv
CYBER_RISK_STORAGE=sqlite
```

5. Confira antes de iniciar:

```powershell
docker compose config
docker compose up -d --force-recreate
docker compose ps
docker compose exec api python -c "import os; print(os.environ['CYBER_RISK_STORAGE'], os.environ['CYBER_RISK_DB'])"
(Invoke-RestMethod http://127.0.0.1:8000/ativos).Count
```

Deve mostrar o número de ativos esperado (por exemplo 6, se o JSON não tiver mudado). Teste também `/ui/`, `/health` e `/diario`.

**Nunca execute `docker compose down -v` neste fluxo**: `-v` remove o volume de dados. `down` sem `-v` preserva o volume nomeado.

O Diário da Caçada continua no arquivo `/dados/ativos_diario.jsonl`, separado do inventário SQLite. Não é migrado por este processo.

### Música na interface

Se `frontend/assets/audio/laurence.mp3` estiver excluído da imagem por direitos autorais, não será incluído no rebuild. Para uso local autorizado, é necessário disponibilizar o arquivo de forma separada, sem versioná-lo nem distribuí-lo no pacote.

## 6. Testes e checkpoint

```powershell
python -m pytest tests/test_migracao_ativacao_sqlite.py -v
python -m pytest -q
git status
git diff --check
```

Quando os testes passarem, revise tudo que será salvo:

```powershell
git add infraestrutura/seletor_repositorio.py scripts/migrar_json_para_sqlite.py tests/test_migracao_ativacao_sqlite.py api/app.py compose.yaml dockerfile .dockerignore docs/ativacao_sqlite_api_docker.md
git diff --cached --stat
git diff --cached --check
git commit -m "Integra armazenamento SQLite opcional na API e Docker"
git push origin feature/banco-dados
```

Não inclua bancos SQLite, inventários locais, JSONL, backups, `.env` ou arquivos de mídia protegida. Não faça merge na `main` antes de concluir os testes e as verificações de execução em ambos os modos.
