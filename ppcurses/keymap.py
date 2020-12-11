import ppcurses.errors
import logging

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
    if pstate._name != 'header':
        state = pstate
    return state


@key('l')
def navright(state):
    return getattr(state, 'nstate', state)


@key('r')
def refresh(state):
    state.update()
    return state


def do(state, key):
    try:
        state = REGISTERED[key](state)
    except KeyError:
        logger.warning('Unregistered key press detected - %s', key)
    return state
