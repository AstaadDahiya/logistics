FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY services/ ./services/
COPY shared/ ./shared/

RUN pip install --no-cache-dir hatchling
RUN pip install --no-cache-dir .

CMD ["python", "-m", "services.prediction.context_assembly"]
