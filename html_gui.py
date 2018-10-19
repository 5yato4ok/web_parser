from flask import Flask, g, session, flash, redirect, url_for, abort, request, render_template
from main import Gipfel_Parser
import sys
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"  # return a string

@app.route('/parser',methods = ['POST', 'GET'])
def welcome():
    if request.method == 'POST':
        smth =2
    elif request.method == 'GET':
        return render_template('parser.html')  # render a template

if __name__ == '__main__':
    app.run(debug=True)