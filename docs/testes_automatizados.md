
# Testes Automatizados — Cyber Risk Engine

## Objetivo

Validar automaticamente os principais componentes
do Cyber Risk Engine utilizando pytest.

## Ferramentas

- Python
- pytest
- FastAPI TestClient
- NumPy

## Componentes testados

| Arquivo | Testes |
|---|---:|
| tests/test_api.py | 11 |
| tests/test_inventario.py | 7 |
| tests/test_vulnerabilidades.py | 7 |
| tests/test_modelo_risco.py | 9 |
| **Total** | **34** |

## Execução

Na raiz do projeto:

```powershell
python -m pytest -v
```

## Resultado

34 testes aprovados em 0,61 segundo.

Foi registrado um aviso de descontinuação
relacionado à integração entre FastAPI,
Starlette e httpx, sem falhas nos testes.

## Isolamento dos testes

Os testes utilizam objetos de inventário
independentes e arquivos JSON temporários,
preservando o arquivo ativos.json do projeto.

## Modelo matemático

Foram validados:

- Dimensões das matrizes.
- Cálculo do risco próprio.
- Tratamento de vulnerabilidades corrigidas.
- Construção da matriz de dependências.
- Cálculo do risco efetivo.
- Equação matricial (I - A)x = b.
- Inventário vazio.
- Dependências inexistentes.
- Identificação de matriz singular.

## Conclusão

Os 34 testes automatizados foram aprovados
nos cenários avaliados, oferecendo uma base
de regressão para futuras alterações.
```
