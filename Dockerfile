FROM python:3.11.8-slim

RUN apt-get update && \
    apt-get install -y gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY images /app/images
COPY database /app/database
COPY .env /app/.env
COPY .flaskenv /app/.flaskenv


EXPOSE 80

CMD ["python", "src/main.py", "--config", "production"]
