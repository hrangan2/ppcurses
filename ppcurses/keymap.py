import ppcurses.errors
import ppcurses.state
from ppcurses import global_state, domain
import logging
import subprocess

logger = logging.getLogger(__name__)


REGISTERED = {}


def key(k):
    def inner(func):
        if k in REGISTERED:
            raise ppcurses.errors.DuplicateKeyDefined(k, func.__name__)
        REGISTERED[k] = func
        REGISTERED[k.upper()] = func

        def inner2(state):
            return func(state)
        return inner2
    return inner


@key('q')
def quit(state):
    logger.info('Pressed q')
    raise ppcurses.errors.GracefulExit


@key('k')
def navup(state):
    state.prev()
    return state


@key('j')
def navdown(state):
    state.next()
    return state


@key('h')
def navleft(state):
    pstate = getattr(state, 'pstate', state)
    state.active = False
    state.window.draw()
    if getattr(pstate, 'name') != 'header':
        state = pstate
    state.active = True
    state.window.draw()
    return state


@key('l')
def navright(state):
    state.active = False
    state.window.draw()
    state = getattr(state, 'nstate', state)
    state.active = True
    state.window.draw()
    return state


@key('r')
def refresh(state):
    state.update()
    return state


@key('i')
def add_comment(state):
    state.add_comment()
    return state


@key('y')
def yank_card_url(state):
    if global_state['card'].id is not None:
        direct_link = f"https://{domain}/#direct/card/{global_state['card'].id}"
    else:
        direct_link = ''
    subprocess.run("pbcopy", universal_newlines=True, input=direct_link)
    return state


def do(state, key):
    if key not in REGISTERED:
        logger.warning('Unregistered key press detected - %s', repr(key))
    else:
        state = REGISTERED[key](state)
    return state
