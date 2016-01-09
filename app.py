# coding=utf-8
from flask import Flask, render_template, request
import simplejson

from light_scrapper_web_api import LightScrapAPI

app = Flask(__name__)
app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get/chapters/', methods=['POST'])
def walk():
    scrapper = LightScrapAPI(title=request.form['title'],
                             start_chapter_number=request.form['start'],
                             end_chapter_number=request.form['end'],
                             url=request.form['url'])
    return simplejson.dumps(scrapper.get_chapters_as_json(), cls=simplejson.encoder.JSONEncoderForHTML)


if __name__ == '__main__':
    app.run()
