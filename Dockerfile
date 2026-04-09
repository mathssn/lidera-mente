FROM python:3.11-slim

# Evita gerar arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# (Opcional, mas bom garantir)
RUN update-ca-certificates

# Copiar dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]