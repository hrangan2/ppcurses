import curses
import ppcurses.errors
import ppcurses.start
import ppcurses.state
import ppcurses
import logging
import subprocess

logger = logging.getLogger(__name__)


REGISTERED = {}


def key(k):
    def inner(func):
        if k in REGISTERED:
            raise ppcurses.errors.DuplicateKeyDefined(k, func.__name__)
        REGISTERED[ord(k)] = func

        def inner2(state):
            return func(state)
        return inner2
    return inner


@key('c')
def change_project_board(state):
    ppcurses.start.select_project_board()
    ppcurses.memstore['header'].update()
    return state


@key('q')
def quit(state):
    logger.info('Pressed q')
    raise ppcurses.errors.GracefulExit


@key('h')
@key(chr(curses.KEY_LEFT))
def navleft(state):
    pstate = getattr(state, 'pstate', state)
    state.active = False
    state.window.draw()
    if getattr(pstate, 'name') != 'header':
        state = pstate
    state.active = True
    state.window.draw()
    return state


@key('j')
@key(chr(curses.KEY_DOWN))
def navdown(state):
    state.next()
    return state


@key('k')
@key(chr(curses.KEY_UP))
def navup(state):
    state.prev()
    return state


@key('l')
@key(chr(curses.KEY_RIGHT))
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
    if ppcurses.storage['card_id'] is not None:
        direct_link = f"https://{ppcurses.domain}/#direct/card/{ppcurses.storage['card_id']}"
    else:
        direct_link = ''
    subprocess.run("pbcopy", universal_newlines=True, input=direct_link)
    return state


def do(state, key, allowed_keys=['*']):
    if ('*' not in allowed_keys) and (key not in [ord(c) for c in allowed_keys]):
        logger.info('Skipping blocked key - %s', repr(key))
        return state
    if key not in REGISTERED:
        logger.warning('Unregistered key press detected - %s', repr(key))
    else:
        state = REGISTERED[key](state)
    return state
