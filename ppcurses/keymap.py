import ppcurses.errors
import ppcurses.state
import ppcurses.utils
import logging
import subprocess

logger = logging.getLogger(__name__)


REGISTERED = {}


def key(k):
    def inner(func):
        if k in REGISTERED:
            raise ppcurses.errors.DuplicateKeyDefined(k, func.__name__)
        REGISTERED[k] = func

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


@key('y')
def yank_card_url(state):
    subprocess.run("pbcopy", universal_newlines=True, input=ppcurses.utils.direct_card_link())
    return state


def do(state, key):
    if key not in REGISTERED:
        logger.warning('Unregistered key press detected - %s', repr(key))
    else:
        state = REGISTERED[key](state)
    return state
