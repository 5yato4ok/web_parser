    #!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, Response,request, render_template
from main import Nix_Parser, mutex, cur_text
import sys
from threading import Thread, Event,Lock

import time

app = Flask(__name__)

thread = Thread()
thread_stop_event = Event()

result_file_name = 'result.xml'
parsing_over = False

class ParsingThread(Thread):
    is_daily = False
    timeout = 0
    is_logging=False
    socket = None
    parser = None
    def __init__(self,daily,timeout_,is_logging_):
        self.delay = 1
        super(ParsingThread, self).__init__()
        self.is_daily=daily
        self.timeout = timeout_
        self.is_logging = is_logging_
        self._stop_event = Event()
        self.parser = Nix_Parser('https://www.nix.ru/', 'https://www.nix.ru/price/index.html',
                                 self.timeout, self.is_logging)

    def stopped(self):
        return self._stop_event.is_set()

    def run_parser(self):
        global parsing_over
        parsing_over = False
        print("Start task")
        try:
            self.parser.parse_catalog()
            print("Finished parsing")
            self.parser.write_to_txml(result_file_name)
            parsing_over = True
        except:
            parsing_over=True
            print("Eror while parsing")

    def stop(self):
        self._stop_event.set()

    def run(self):
        if self.is_daily:
            while True and not self.stopped():
                self.run_parser()
                time.sleep(86400) #sleep a day
        else:
            self.run_parser()

class Tee(object):
    def write(self, obj):
        global cur_text
        cur_text += str(obj)
        #with app.app_context():
        #    return render_template('parser.html',output=cur_text)
        #socketio.emit('newText',{'text':cur_text},namespace='/')

@app.route('/result')
def open_file():
    with open(result_file_name,'rb') as result:
        return Response(result.read(), mimetype='text/plain')


@app.route('/close')
def close():
    sys.exit(0)

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
    global thread
    if thread.isAlive():
        thread.stop()
    thread=ParsingThread(is_daily,timeout,is_logging)
    thread.start()
    return render_template('parser.html', output=cur_text)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5001)
    #app.run(debug=True)
    parser = Nix_Parser('https://www.nix.ru/', 'https://www.nix.ru/price/index.html', 60, True)
    try:
        parser.parse_catalog()
        print("Finished parsing")
        parser.write_to_txml('result_file.xml')
    except Exception as e:
        print("Error parsing")
        print(e)
        parser.write_to_txml('result_file_error.xml')

