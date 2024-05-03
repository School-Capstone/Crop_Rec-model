web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
release: heroku run alembic upgrade head