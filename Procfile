web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
init: alembic init alembic
migrate: alembic revision --autogenerate -m "New Migration"
upgrade: heroku run alembic upgrade head