# coding=utf-8
import json
import urllib2

from webapp import app
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


@app.route('/task/<id>')
def task_info(id):
    task = Task.query.get(id)
    return json.dumps({'id': id, 'task': {
        'start': task.start,
        'end': task.end,
        'current': task.current
    }})


@app.route('/task/<id>/chapters')
def chapter_info(id):
    return json.dumps({'id': id, 'chapters': Chapter.filter.query(Chapter.task == id)})

