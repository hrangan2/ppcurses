#!/usr/bin/env python
import time
import pickle
import sqlite3
import os
import requests
from datetime import datetime
from dateutil import tz
from ppcurses.errors import CallFailure
import logging
import configparser

mode = 'ppcurses'

logging.basicConfig(filename='ppcurses.log', level=logging.INFO)
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
domain=service.projectplace.com
""")

parser = configparser.ConfigParser()
parser.read_file(open(configfile))
token = parser.get(mode, 'token')
if token == 'ADD_USER_TOKEN':
    print('Add your projectplace token to %s' % configfile)
    exit()
domain = parser.get(mode, 'domain')


def _get(endpoint):
    logger.info('Calling endpoint GET %s', endpoint)
    memstore['statuswin'].set('updating')
    url = 'https://' + domain + endpoint
    r = requests.get(url, headers={'Authorization': 'Bearer ' + token})
    memstore['statuswin'].unset()

    if not r.ok:
        logger.error("Failed calling %s, [%s]", (endpoint, r.status_code))
        raise CallFailure(r.status_code, endpoint)
    else:
        return r.json()


def get(endpoint, refetch=False):
    if refetch or (endpoint not in dbstore):
        dbstore[endpoint] = _get(endpoint)
    return dbstore[endpoint]


def delete(endpoint):
    logger.info('Calling endpoint DELETE %s', endpoint)
    url = 'https://' + domain + endpoint
    r = requests.delete(url, headers={'Authorization': 'Bearer ' + token})
    if r.ok:
        return True
    else:
        logger.warning("Failed deleting %s, [%s]", (endpoint, r.status_code))
        return False


def put(endpoint, data):
    logger.info('Calling endpoint PUT %s', endpoint)
    url = 'https://' + domain + endpoint
    r = requests.put(url, json=data, headers={'Authorization': 'Bearer ' + token})
    if r.ok:
        return True
    else:
        logger.error("Failed updating %s, [%s]", (endpoint, r.status_code))
        return False


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


def memoize(func):
    def inner(kwargs):
        key = str(sorted(kwargs.items(), key=lambda x: x[0]))
        if key not in memstore:
            memstore[key] = func(kwargs)
        return memstore[key]
    return inner


class KeyValueDB:
    _cache = {}

    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(internaldir, '%s.db' % mode))
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
