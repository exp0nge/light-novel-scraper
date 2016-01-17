web: python run.py --log-file=-
worker: redis-server
celery: celery -A webapp.celery worker --loglevel=INFO
