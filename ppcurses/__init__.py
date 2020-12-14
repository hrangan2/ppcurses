#!/usr/bin/env python
import pickle
import sqlite3
import os
import requests
from datetime import datetime
from dateutil import tz
from ppcurses.errors import CallFailure
import logging
import configparser


logger = logging.getLogger(__name__)


internaldir = os.path.join(os.path.expanduser('~'), '.ppcurses')
configfile = os.path.join(internaldir, 'config')
if not os.path.exists(internaldir):
    os.mkdir(internaldir)
if not os.path.exists(configfile):
    with open(configfile, 'w') as f:
        f.write("""\
[ppcurses]
token=ADD_USER_TOKEN
domain=local.rnd.projectplace.com
api_domain=api-local.rnd.projectplace.com
""")

parser = configparser.ConfigParser()
parser.read_file(open(configfile))
token = parser.get('ppcurses', 'token')
if token == 'ADD_USER_TOKEN':
    print('Add your projectplace token to %s' % configfile)
    exit()
domain = parser.get('ppcurses', 'domain')
api_domain = parser.get('ppcurses', 'api_domain')


def get(endpoint='/'):
    logger.info('Calling endpoint %s', endpoint)
    url = 'https://' + api_domain + endpoint
    r = requests.get(url, headers={'Authorization': 'Bearer ' + token})

    if not r.ok:
        logger.error("Failed calling %s, [%s]", (endpoint, r.status_code))
        raise CallFailure(r.status_code, endpoint)
    else:
        return r.json()


def epoch_to_datetime(epoch_ts):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.utcfromtimestamp(epoch_ts)
    utc = utc.replace(tzinfo=from_zone)

    dest = utc.astimezone(to_zone)
    return dest.strftime('%c')


def link(*states):
    """ You need to pass a list of states to this function before they can work """
    logger.info('linking %s states', len(states))
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
        self.conn = sqlite3.connect(os.path.join(internaldir, 'ppcurses.db'))
        cursor = self.conn.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS keyval (
                    key text UNIQUE NOT NULL,
                    value text
                )
                """)
        r = cursor.execute("SELECT key, value FROM keyval""")
        for row in r.fetchall():
            self.__class__._cache[row[0]] = pickle.loads(row[1])

    def __setitem__(self, key, value):
        cursor = self.conn.cursor()
        res = cursor.execute("""
                UPDATE keyval SET value=? WHERE key=?
                """, (pickle.dumps(value), key))
        if not res.rowcount:
            cursor.execute("""
                INSERT INTO keyval(key, value) VALUES (?, ?)
                """, (key, pickle.dumps(value)))
        self.__class__._cache[key] = value
        self.conn.commit()

    def __getitem__(self, key):
        try:
            return self.__class__._cache[key]
        except KeyError:
            return None


dbstore = KeyValueDB()
memstore = {}
