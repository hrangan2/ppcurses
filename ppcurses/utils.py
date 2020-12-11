import time
import requests
from collections import defaultdict
from ppcurses import token, domain, api_domain
from ppcurses.errors import CallFailure
import logging

logger = logging.getLogger(__name__)


TIMING = defaultdict(list)


def timeit(func):
    def inner(*args, **kwargs):
        start = time.time()
        retval = func(*args, **kwargs)
        taken = time.time() - start
        TIMING[func.__name__].append((str(taken) + ' ' + str(args) + ',' + str(kwargs)))
        return retval
    return inner


@timeit
def get(endpoint):
    logger.info('Calling endpoint %s', endpoint)
    url = 'https://' + api_domain + endpoint
    r = requests.get(url, headers={'Authorization': 'Bearer ' + token})

    if not r.ok:
        logger.error("Failed calling %s, [%s]", (endpoint, r.status_code))
        raise CallFailure(r.status_code, endpoint)
    else:
        return r.json()


def direct_card_link():
    if global_state['card_id'] is not None:
        return f"https://{domain}/#direct/card/{global_state['card_id']}"
    else:
        return ''


global_state = {}
