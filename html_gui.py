#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for, abort, request, render_template, current_app
from main import Gipfel_Parser
import sys
from celery import Celery
import time


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
cur_text = "Result of parsing:\n"


class Tee(object):
    def write(self, obj):
        global cur_text
        cur_text += str(obj)
        with app.app_context():
            return render_template('parser.html',output=cur_text)

@celery.task
def parsing():
    test_class = Gipfel_Parser('https://gipfel.ru', 'https://gipfel.ru/catalog', timeout_, is_logging_)
    test_class.parse_catalog()
    test_class.write_to_txml('result.xml')


@app.route('/',methods = ['POST', 'GET'])
def index():
    sys.stdout = Tee()
    if request.method == 'GET':
        return render_template('parser.html', output=cur_text)  # render a template
    timeout = int(request.form['timeout'])
    is_logging = None
    if 'is_logging' in request.form:
        if request.form['is_logging']=='on':
            is_logging = True
        else:
            is_logging = False
    is_daily=None
    if 'is_daily' in request.form:
        if request.form['is_daily']=="on":
            is_daily = True
        else:
            is_daily = True
    print("Start parsing")
    task = None
    if is_daily:
        task = parsing.apply_async(args=[timeout, is_logging], countdown=86400)
    else:
        task = parsing.apply_async()
    #start_parsing(timeout,is_logging,is_daily)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

