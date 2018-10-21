    #!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, redirect, url_for, abort, request, render_template, current_app
from flask_socketio import SocketIO, emit
from main import Gipfel_Parser
import sys
from threading import Thread, Event
import time


app = Flask(__name__)
app.config['DEBUG'] = True
socketio = SocketIO(app)
cur_text = "Result of parsing:\n"
thread= Thread()
thread_stop_event = Event()


class ParsingThread(Thread):
    is_daily = False
    timeout = 0
    is_logging=False
    def __init__(self,daily,timeout_,is_logging_):
        self.delay = 1
        super(ParsingThread, self).__init__()
        self.is_daily=daily
        self.timeout = timeout_
        self.is_logging = is_logging_

    def run_parser(self):
        print("Start task")
        test_class = Gipfel_Parser('https://gipfel.ru', 'https://gipfel.ru/catalog', self.timeout, self.is_logging)
        test_class.parse_catalog()
        test_class.write_to_txml('result.xml')
        

    def run(self):
        if self.is_daily:
            while True:
                self.run_parser()
                time.sleep(86400) #sleep a day
        else:
            self.run_parser()

@socketio.on('my event')                          
def test_message(message):                        
    emit('my response', {'data': 'got it!'}) 

class Tee(object):
    def write(self, obj):
        global cur_text
        cur_text += str(obj)
        #with app.app_context():
        #    return render_template('parser.html',output=cur_text)
        socketio.emit('newText',{'text':cur_text},namespace='/')

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
    thread=ParsingThread(is_daily,timeout,is_logging)
    thread.start()
    
    #start_parsing(timeout,is_logging,is_daily)
    return redirect(url_for('index'))

@socketio.on('disconnect', namespace='/')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    #app.run(debug=True)
    socketio.run(app)

