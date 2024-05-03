web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
init: alembic init alembic
upgrade: alembic upgrade head
migrate: alembic revision --autogenerate -m "New Migration1"