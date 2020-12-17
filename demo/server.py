#!/usr/bin/env python
from flask import render_template
from flask import Flask
from words import titles

app = Flask(__name__)


@app.route('/title')
def get_title():
    with open('index') as f:
        index = int(f.read())
    return titles[index]


@app.route('/control')
def control():
    return render_template('control.html')


@app.route('/_reset')
def reset():
    with open('index', 'w') as f:
        f.write('0')
    return ''


@app.route('/_increment')
def increment():
    with open('index') as f:
        index = int(f.read())
    if index == len(titles) - 1:
        return ''
    index += 1
    with open('index', 'w') as f:
        f.write(str(index))
    return ''


@app.route('/_decrement')
def decrement():
    with open('index') as f:
        index = int(f.read())
    if index == 0:
        return
    index -= 1
    with open('index', 'w') as f:
        f.write(str(index))
    return ''


@app.route('/')
def home():
    with open('index', 'w') as f:
        f.write('0')
    return render_template('slide.html')
