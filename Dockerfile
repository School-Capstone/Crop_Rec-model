FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Setup google proxy
RUN curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.11.0/cloud-sql-proxy.linux.amd64
RUN chmod +x cloud-sql-proxy
RUN gcloud sql instances describe premium-valor-418410:us-east1:test-instance
# Run Alembic migrations
RUN alembic upgrade head

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]




# CMD [ "alembic upgrade head && uvicorn server:app --host 0.0.0.0 --port 80" ]
