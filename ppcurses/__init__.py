#!/usr/bin/env python
import time
import pickle
import sqlite3
import os
import requests
from datetime import datetime
from dateutil import tz
from ppcurses.errors import CallFailure
import ppcurses.auth
import logging
import configparser

mode = ''
configname = f'ppcurses_{mode}' if mode else 'ppcurses'
os.environ.setdefault('ESCDELAY', '25')

internaldir = os.path.join(os.path.expanduser('~'), '.ppcurses')
logging.basicConfig(filename=os.path.join(internaldir, 'ppcurses.log'), level=logging.INFO)
logger = logging.getLogger(__name__)


configfile = os.path.join(internaldir, 'config')
if not os.path.exists(internaldir):
    os.mkdir(internaldir)
if not os.path.exists(configfile):
    with open(configfile, 'w') as f:
        f.write("""\
[ppcurses]
token=ADD_USER_TOKEN
domain=service.projectplace.com
""")

parser = configparser.ConfigParser()
parser.read_file(open(configfile))
token = parser.get(configname, 'token', None)
if not ppcurses.auth.validate_token(token):
    input('Press any button to authenticate ppcurses through the browser')
    ppcurses.auth.login()
domain = parser.get(configname, 'domain')


def _get(endpoint):
    logger.info('Calling endpoint GET %s', endpoint)
    memstore['statuswin'].set('updating')
    url = 'https://' + domain + endpoint
    r = requests.get(url, headers={'Authorization': 'Bearer ' + token})
    memstore['statuswin'].unset()

    if r.status_code in (401, 403):
        ppcurses.auth.refresh_token()
    elif not r.ok:
        logger.error("Failed calling %s, [%s]", (endpoint, r.status_code))
        raise CallFailure(r.status_code, endpoint)
    else:
        return r.json()


def get(endpoint, refetch=False):
    if refetch or (endpoint not in dbstore):
        dbstore[endpoint] = _get(endpoint)
    return dbstore[endpoint]


def delete(endpoint, _=None):
    logger.info('Calling endpoint DELETE %s', endpoint)
    url = 'https://' + domain + endpoint
    r = requests.delete(url, headers={'Authorization': 'Bearer ' + token})
    if r.ok:
        return r.json()
    else:
        logger.warning("Failed deleting %s, [%s]", (endpoint, r.status_code))
        return False


def put(endpoint, data):
    logger.info('Calling endpoint PUT %s', endpoint)
    url = 'https://' + domain + endpoint
    r = requests.put(url, json=data, headers={'Authorization': 'Bearer ' + token})
    if r.ok:
        return r.json()
    else:
        logger.error("Failed updating %s, [%s]", (endpoint, r.status_code))
        return False


def put_form(endpoint, data):
    logger.info('Calling endpoint PUT %s', endpoint)
    url = 'https://' + domain + endpoint
    r = requests.put(url, data=data, headers={'Authorization': 'Bearer ' + token})
    if r.ok:
        return r.json()
    else:
        logger.error("Failed updating %s, [%s]", (endpoint, r.status_code))
        return False


def post(endpoint, data):
    logger.info('Calling endpoint POST %s', endpoint)
    url = 'https://' + domain + endpoint
    r = requests.post(url, json=data, headers={'Authorization': 'Bearer ' + token})
    if r.ok:
        return r.json()
    else:
        logger.error("Failed updating %s, [%s]", (endpoint, r.status_code))
        return False


def post_form(endpoint, data):
    logger.info('Calling endpoint POST %s', endpoint)
    url = 'https://' + domain + endpoint
    r = requests.post(url, data=data, headers={'Authorization': 'Bearer ' + token})
    if r.ok:
        return r.json()
    else:
        logger.error("Failed updating %s, [%s]", (endpoint, r.status_code))
        return False


def mkundo(state, action, endpoint, data=None):
    memstore['undo_args'] = {
            'action': lambda: action(endpoint, data),
            'state': state,
            'timestamp': time.time()
            }


def epoch_to_datetime(epoch_ts):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.utcfromtimestamp(epoch_ts)
    utc = utc.replace(tzinfo=from_zone)

    dest = utc.astimezone(to_zone)
    return dest.strftime('%c')


def link(*states):
    """ You need to pass a list of states to this function before they can work """
    logger.info('linking states %s', repr(states))
    for n, each in enumerate(states):
        if n:
            each.pstate = states[n-1]
        try:
            each.nstate = states[n+1]
        except IndexError:
            pass


class KeyValueDB:
    _cache = {}

    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(internaldir, '%s.db' % configname))
        cursor = self.conn.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS keyval (
                    key text UNIQUE NOT NULL,
                    value text,
                    timestamp integer
                )
                """)
        age_7days = int(time.time()) - 7*24*60*60
        cursor.execute("DELETE FROM keyval WHERE timestamp < ?", (age_7days, ))
        self.reload()

    def reload(self):
        self.__class__._cache = {}
        cursor = self.conn.cursor()
        r = cursor.execute("SELECT key, value FROM keyval""")
        for row in r.fetchall():
            self.__class__._cache[row[0]] = pickle.loads(row[1])

    def set_forever(self, key, value):
        cursor = self.conn.cursor()
        res = cursor.execute("""
                UPDATE keyval SET value=?, timestamp=null WHERE key=?
                """, (pickle.dumps(value), key))
        if not res.rowcount:
            cursor.execute("""
                INSERT INTO keyval(key, value) VALUES (?, ?)
                """, (key, pickle.dumps(value)))
        self.__class__._cache[key] = value
        self.conn.commit()

    def clear_transient(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM keyval WHERE timestamp IS NOT NULL
        """)
        self.conn.commit()
        self.reload()

    def __setitem__(self, key, value):
        cursor = self.conn.cursor()
        timestamp = int(time.time())
        res = cursor.execute("""
                UPDATE keyval SET value=?, timestamp=? WHERE key=?
                """, (pickle.dumps(value), timestamp, key))
        if not res.rowcount:
            cursor.execute("""
                INSERT INTO keyval(key, value, timestamp) VALUES (?, ?, ?)
                """, (key, pickle.dumps(value), timestamp))
        self.__class__._cache[key] = value
        self.conn.commit()

    def __contains__(self, key):
        return key in self.__class__._cache

    def __getitem__(self, key):
        try:
            return self.__class__._cache[key]
        except KeyError:
            return None


dbstore = KeyValueDB()
memstore = {}
