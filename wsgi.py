# coding=utf-8
from webapp import app, db

db.create_all()

app.run()
