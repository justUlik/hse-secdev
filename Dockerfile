FROM python:3.11.6-slim AS build

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt


COPY app ./app

FROM python:3.11.6-slim

WORKDIR /app

RUN useradd -m -u 10001 appuser
RUN chown -R appuser:appuser /app

COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin

COPY app ./app

RUN mkdir -p /app/logs && chown -R 10001:10001 /app/logs

    EXPOSE 8000

HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health')" || exit 1

USER appuser
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
