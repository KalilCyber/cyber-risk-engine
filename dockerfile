
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

# Porta utilizada pela API HTTP
EXPOSE 8000

# Inicia o Cyber Risk Engine como serviço HTTP
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
