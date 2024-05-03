web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
init: alembic init alembic
migrate: alembic revision --autogenerate -m "New Migration"
release: heroku run alembic upgrade head