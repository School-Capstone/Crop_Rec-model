FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN alembic upgrade head

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
