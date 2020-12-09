import time
import requests
from collections import defaultdict
from ppcurses import token, domain
from ppcurses.errors import CallFailure


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
    url = 'https://' + domain + endpoint
    r = requests.get(url, headers={'Authorization': 'Bearer ' + token})
    if not r.ok:
        raise CallFailure(r.status_code, endpoint)
    else:
        return r.json()
