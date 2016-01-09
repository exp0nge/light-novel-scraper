# coding=utf-8
from webapp import db


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_number = db.Column(db.Integer, autoincrement=False)
    url = db.Column(db.String(200))
    content = db.Column(db.Text)
    task = db.Column(db.String(36))

    def __init__(self, task, chapter_number, url, content):
        self.chapter_number = chapter_number
        self.url = url
        self.content = content
        self.task = task
