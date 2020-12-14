import requests
from datetime import datetime
from dateutil import tz
from ppcurses import token, domain, api_domain
from ppcurses.errors import CallFailure
import logging

logger = logging.getLogger(__name__)


def get(endpoint='/'):
    logger.info('Calling endpoint %s', endpoint)
    url = 'https://' + api_domain + endpoint
    r = requests.get(url, headers={'Authorization': 'Bearer ' + token})

    if not r.ok:
        logger.error("Failed calling %s, [%s]", (endpoint, r.status_code))
        raise CallFailure(r.status_code, endpoint)
    else:
        return r.json()


def direct_card_link():
    if global_state['card'].id is not None:
        return f"https://{domain}/#direct/card/{global_state['card'].id}"
    else:
        return ''


def epoch_to_datetime(epoch_ts):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.utcfromtimestamp(epoch_ts)
    utc = utc.replace(tzinfo=from_zone)

    dest = utc.astimezone(to_zone)
    return dest.strftime('%c')


global_state = {}
