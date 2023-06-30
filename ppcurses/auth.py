import logging
import uuid
import requests
import ulimi.config
import ulimi.exceptions
from urllib.parse import urlencode, urlparse, urlunparse
from flask import Flask, request, abort, session, url_for, redirect
import ulimi.db
try:
    import ulimi.secrets
except ImportError:
    ulimi.secrets = None


logger = logging.getLogger(__name__)


app = Flask.app(__name__)
# app.run(host="0.0.0.0", port=4987)


def build_query(url, params):
    url_parts = list(urlparse(url))
    url_parts[4] = urlencode(params)
    return urlunparse(url_parts)


def get_github_user_from_token(token):
    headers = {"Authorization": f"token {token}"}
    r = requests.get("https://api.github.com/user""", headers=headers)
    if r.status_code == 401:
        raise ulimi.exceptions.Github401
    return r.json()['login']


def validate_token(token):
    if token in ('ADD_USER_TOKEN', None):
        return False


def refresh_token(token):
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    global state
    state = uuid.uuid4().hex
    body = {
        "client_id": ulimi.secrets.github_client_id,
        "redirect_uri": login_redirect,
        "scope": "repo user:email",
        "state": state,
        "allow_signup": False
    }
    url = ulimi.config.github_authorize_url
    return redirect(build_query(url, body))


@routes.route('/callback')
def login_callback():
    global state
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


@routes.route('/logout', methods=['GET', 'POST'])
def logout():
    username = session.pop('username', None)
    if username:
        ulimi.db.delete_github_token(username)
    return redirect(url_for('index'))
