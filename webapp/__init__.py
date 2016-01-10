# coding=utf-8
# coding=utf-8
from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['EPUB_FOLDER'] = os.path.abspath('epubs')

if not os.path.isdir(app.config['EPUB_FOLDER']):
    os.makedirs(app.config['EPUB_FOLDER'])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'


db = SQLAlchemy(app)


def make_celery(app):
    celery = Celery(app.import_name,
                    broker=app.config['CELERY_BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)

import webapp.views
