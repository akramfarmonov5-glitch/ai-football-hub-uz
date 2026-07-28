FROM python:3.13-slim

# Python: .pyc yozmaslik, log'lar darhol chiqishi
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Bog'liqliklar alohida qatlamda — kod o'zgarganda qayta o'rnatilmaydi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# root emas, oddiy foydalanuvchi ostida ishlaydi
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Render va shunga o'xshash hostinglar portni PORT o'zgaruvchisi orqali beradi;
# lokal ishga tushirishda 8000 ishlatiladi.
ENV PORT=8000
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os,urllib.request,sys; sys.exit(0 if urllib.request.urlopen(f\"http://localhost:{os.environ.get('PORT','8000')}/health\", timeout=4).status == 200 else 1)"

# Shell shakli ataylab: $PORT kengayishi uchun
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
