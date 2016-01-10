web: python run.py --log-file=-
worker: redis-server
worker: celery -A webapp.celery worker --loglevel=INFO
