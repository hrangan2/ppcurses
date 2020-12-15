import curses
import inspect
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
        if len(k) == 1:
            if k in REGISTERED:
                raise ppcurses.errors.DuplicateKeyDefined(k, func.__name__)
            REGISTERED[ord(k)] = func
        else:
            partial = REGISTERED
            for n, char in enumerate(k):
                if n == (len(k) - 1):
                    if callable(partial):
                        raise ppcurses.errors.RootKeyExists(k, func.__name__)
                    if ord(char) in partial:
                        raise ppcurses.errors.DuplicateKeyDefined(k, func.__name__)
                    partial[ord(char)] = func
                else:
                    if ord(char) not in partial:
                        partial[ord(char)] = {}
                    partial = partial[ord(char)]

        def inner2(state):
            return func(state)
        return inner2
    return inner


@key('ac')
def write_comment(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('xc')
def delete_comment(state):
    k = ppcurses.memstore['statuswin'].getch()
    if chr(k).isdigit():
        change = ppcurses.memstore['comments'].delete(int(chr(k)))
        if change:
            ppcurses.memstore['comments'].update(cascade=False, reset_position=True, refetch=True)
    return state


@key('ec')
def edit_comment(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('ct')
def change_title(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('cd')
def change_description(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('cp')
def change_points(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('cl')
def change_label(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('ca')
def change_assignee(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('cc')
def change_co_assignee(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('tl')
def toggle_checklist(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('el')
def edit_checklist(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('al')
def add_checklist(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key('xl')
def delete_checklist(state):
    k = ppcurses.memstore['statuswin'].getch()
    if chr(k).isdigit():
        index = int(chr(k))
        change = ppcurses.memstore['card'].delete_checklist(index)
        if change:
            ppcurses.memstore['card'].update(cascade=False, reset_position=True, refetch=True)
    return state


@key('vl')
def checklist_to_card(state):
    logger.error('Pending command - %s' % inspect.stack()[0][3])
    return state


@key(chr(curses.KEY_RESIZE))
def resize_term(state):
    logger.warning("Terminal resize detected")
    return state


@key('s')
def change_project_board(state):
    ppcurses.start.select_project_board()
    ppcurses.memstore['header'].update(reset_position=True)
    return state


@key('q')
def quit(state):
    raise ppcurses.errors.GracefulExit


@key('h')
@key(chr(curses.KEY_LEFT))
def navleft(state):
    pstate = getattr(state, 'pstate', state)
    state.deactivate()
    state.window.draw()
    if getattr(pstate, 'name') != 'header':
        state = pstate
    state.activate()
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
    state.deactivate()
    state.window.draw()
    state = getattr(state, 'nstate', state)
    state.activate()
    state.window.draw()
    return state


@key('r')
def refresh(state):
    state.update(refetch=True)
    return state


@key('R')
def refresh_all(state):
    ppcurses.memstore['header'].update(refetch=True)
    return state


@key('y')
def yank_card_url(state):
    if ppcurses.memstore['card_id'] is not None:
        direct_link = f"https://{ppcurses.domain}/#direct/card/{ppcurses.memstore['card_id']}"
    else:
        direct_link = ''
    subprocess.run("pbcopy", universal_newlines=True, input=direct_link)
    return state


def do(state, key, allowed_keys=['*'], keymap=REGISTERED):
    if ('*' not in allowed_keys) and (key not in [ord(c) for c in allowed_keys]):
        ppcurses.memstore['statuswin'].unset()
        logger.info('Skipping blocked key - %s', repr(key))
        return state
    if key not in keymap:
        ppcurses.memstore['statuswin'].unset()
        logger.warning('Unregistered key press detected - %s', repr(key))
    else:
        if callable(keymap[key]):
            state = keymap[key](state)
            ppcurses.memstore['statuswin'].unset()
        else:
            ppcurses.memstore['statuswin'].set(chr(key))
            k = ppcurses.memstore['statuswin'].getch()
            state = do(state, k, keymap=keymap[key])
    return state
