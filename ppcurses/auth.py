#!/usr/bin/env python
import logging
import uuid
import requests
from flask import Flask, request, abort, session, url_for, redirect
try:
    import config
except ImportError:
    print_oauth_instructions()
    exit()


logger = logging.getLogger(__name__)


app = Flask.app(__name__)
state = None


def print_oauth_instructios():
    pass


def build_query(url, params):
    request = requests.models.PreparedRequest()
    request.prepare_url(url, params)
    return request.url


@app.route('/login', methods=['GET', 'POST'])
def login():
    global state
    state = uuid.uuid4().hex
    body = {
        "client_id": config.CLIENT_ID,
        "redirect_uri": "http://localhost:4987/callback",
        "state": state,
    }
    return redirect(build_query(url, body))


@app.route('/callback')
def login_callback():
    if state != request.args.get("state"):
        abort(401, "State mismatch")

    body = {
            "client_id": ulimi.secrets.github_client_id,
            "client_secret": ulimi.secrets.github_client_secret,
            "code": request.args.get("code")
        }
    headers = {
        "Accept": "application/json"
    }
    r = requests.post(ulimi.config.github_access_token_url, headers=headers, data=body)
    if r.ok:
        access_token = r.json()['access_token']
        github_user = get_github_user_from_token(access_token)
        ulimi.db.insert_github_token(github_user, access_token)
        session['username'] = github_user
        return redirect(url_for('index'))
    else:
        abort(401, "Failed to swap auth code for the access token")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    username = session.pop('username', None)
    if username:
        ulimi.db.delete_github_token(username)
    return redirect(url_for('index'))


app.run(host="0.0.0.0", port=4987)
