
# Imagem base com Python 3.14
FROM python:3.14-slim

# Configurações do ambiente Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .

RUN python -m pip install --no-cache-dir -r requirements.txt

# Copia a estrutura da aplicação
COPY api/ ./api/
COPY cliente/ ./cliente/
COPY dominio/ ./dominio/
COPY frontend/ ./frontend/
COPY infraestrutura/ ./infraestrutura/
COPY interface/ ./interface/
COPY servicos/ ./servicos/
COPY tests/ ./tests/
COPY main.py .
COPY scripts/ ./scripts/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Cria usuario e grupo exclusivos para a aplicacao
RUN groupadd --system --gid 10001 cyberrisk \
    && useradd --system --uid 10001 --gid 10001 \
       --no-log-init --no-create-home \
       --shell /usr/sbin/nologin cyberrisk \
    && mkdir -p /dados \
    && chown cyberrisk:cyberrisk /dados

# Executa a aplicacao sem privilegios de root
USER cyberrisk:cyberrisk

# Porta utilizada pela API HTTP
EXPOSE 8000

# Inicia o Cyber Risk Engine como serviço HTTP
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
