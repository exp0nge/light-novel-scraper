# coding=utf-8
import json
import urllib2

from webapp import app, celery
from webapp.models import Chapter
from flask import request, render_template
from light_scrapper_web_api import chapters_walk_task


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/task/', methods=['POST'])
def task():
    try:
        # scrapper.chapters_walk.delay()
        chap_task = chapters_walk_task.delay(title=request.form['title'],
                                             start=request.form['start'],
                                             end=request.form['end'],
                                             url=request.form['url'])
        return json.dumps(str(chap_task))
    except urllib2.URLError:
        return json.dumps({'error': 'invalid url'})


@app.route('/task/<task_id>')
def task_info(task_id):
    return json.dumps({'task': task_id, 'state': celery.AsyncResult(task_id).state})


@app.route('/task/<task_id>/chapters')
def chapter_info(task_id):
    return json.dumps({'task': task_id, 'chapters': [{'chapter': chapter.chapter_number,
                                                      'url': chapter.url,
                                                      'content': chapter.content}
                                                     for chapter in Chapter.query.filter(Chapter.task == task_id)]})
