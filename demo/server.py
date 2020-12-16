#!/usr/bin/env python
from flask import render_template
from flask import Flask

app = Flask(__name__)


titles = [

        "select a project and board on startup",
        "hjkl/arrow keys to navigate columns",
        "add a card with cc",
        "edit the card title with et",
        "edit the card description with ed",
        "add a comment with ac",
        "edit a commeent with ec<n>",

        ]


@app.route('/title')
def get_title():
    with open('index') as f:
        index = int(f.read())
    return titles[index]


@app.route('/r')
def incrementer():
    with open('index') as f:
        index = int(f.read())
    index += 1
    with open('index', 'w') as f:
        f.write(str(index))
    return ''


@app.route('/')
def home():
    with open('index', 'w') as f:
        f.write('0')
    return render_template('slide.html')
