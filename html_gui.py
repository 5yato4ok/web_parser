from flask import Flask, redirect, url_for, abort, request, render_template, current_app
from main import Gipfel_Parser
import threading
import sys
import time
import subprocess

app = Flask(__name__)
cur_text = "Result of parsing:\n"
saved_app = None
thread = None

class Tee(object):
    def write(self, obj):
        global cur_text
        cur_text += str(obj)
        with saved_app.test_request_context():
            return render_template('parser.html',output = cur_text)

@app.route('/')
def home():
    return "Hello, World!"  # return a string

def parsing(timeout_,is_logging_,is_daily):
    test_class = Gipfel_Parser('https://gipfel.ru', 'https://gipfel.ru/catalog', timeout_, is_logging_)
    test_class.parse_catalog()
    test_class.write_to_txml('result.xml')

def start_parsing(timeout_,is_logging_,is_daily):
    print("Start parsing")
    global thread
    thread = threading.Thread(target=parsing,args=(timeout_,is_logging_,is_daily))
    thread.start()
    #return render_template('parser.html',output = cur_text)

@app.route('/parser',methods = ['POST', 'GET'])
def welcome():
    sys.stdout = Tee()
    global saved_app
    saved_app = current_app._get_current_object()
    if request.method == 'POST':
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
        global saved_context
        start_parsing(timeout,is_logging,is_daily)
    return render_template('parser.html',output= cur_text)  # render a template

if __name__ == '__main__':
    app.run(debug=True)

