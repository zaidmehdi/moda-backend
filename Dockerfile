FROM python:3.11.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src /app/src
COPY images /app/images
COPY .env /app/.env


EXPOSE 8080

ENTRYPOINT ["python"]
CMD ["src/main.py"]
