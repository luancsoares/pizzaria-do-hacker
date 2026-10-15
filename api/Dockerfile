# --- Hardening da imagem da API ---
# 1) Imagem base "slim": menos pacotes = menos vulnerabilidades
FROM python:3.14-slim

# 2) Nao gera .pyc (o filesystem sera read-only no Kubernetes) e loga sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 3) Instala dependencias sem cache (imagem menor)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# 4) Usuario sem privilegios: nunca rodar como root
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin pizzaiolo
USER 10001

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
