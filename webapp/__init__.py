# coding=utf-8
from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['EPUB_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epubs')

if not os.path.isdir(app.config['EPUB_FOLDER']):
    os.makedirs(app.config['EPUB_FOLDER'])

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webapp.db'
app.config['BROKER_TRANSPORT'] = "sqlakombu.transport.Transport"
app.config['BROKER_HOST'] = "sqlite:///celerydb.sqlite"
app.config['CELERY_BROKER_URL'] = 'sqla+sqlite:///celerydb.sqlite'
app.config['CELERY_RESULT_BACKEND'] = 'db+sqlite:///results.sqlite'

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
