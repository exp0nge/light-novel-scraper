# coding=utf-8
from webapp import app
import os

app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 33507)))
