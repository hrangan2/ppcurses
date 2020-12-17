import curses
import ppcurses.errors
import ppcurses.hover
import ppcurses.state
import ppcurses
import logging
import pyperclip

logger = logging.getLogger(__name__)


REGISTERED = {}
HELP_MSG = {}


def key(k2):
    def inner(func):
        k = k2.split(' ')[0]
        if func.__doc__ is not None:
            if func.__doc__.strip() not in HELP_MSG:
                HELP_MSG[func.__doc__.strip()] = []
            HELP_MSG[func.__doc__.strip()].append(k2)
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


########################################################################################
#                                   PPCURSES ACTION                                    #
########################################################################################


@key('?')
def help(state):
    "Help"
    parsed = []
    for n, key in enumerate(HELP_MSG):
        logger.error(': '.join([', '.join(HELP_MSG[key]), key]))
        parsed.append({'id': n, 'name': ': '.join([', '.join(HELP_MSG[key]), key])})
    ppcurses.hover.select_one('help', lambda **kwargs: parsed)
    return state


@key('q')
def quit(state):
    """ Quit """
    raise ppcurses.errors.GracefulExit


@key('y')
def yank_card_url(state):
    """ Copy the direct link for a card """
    if ppcurses.memstore['card_id'] is not None:
        direct_link = f"https://{ppcurses.domain}/#direct/card/{ppcurses.memstore['card_id']}"
    else:
        direct_link = ''
    pyperclip.copy(direct_link)
    return state


@key('r')
def refresh(state):
    """ Refresh the current window """
    state.update(refetch=True)
    return state


@key('R')
def refresh_all(state):
    """ Refresh all windows """
    ppcurses.dbstore.clear_transient()
    ppcurses.memstore['headerstate'].update(refetch=True)
    return state


@key('S')
def change_project_board(state):
    """ Change the project and board selection """
    ppcurses.hover.select_project_board()
    ppcurses.memstore['headerstate'].update(reset_position=True)
    return state


@key('u')
def undo(state):
    """ Undo last action """
    change = ppcurses.memstore.get('undo_action', lambda: None)()
    if change:
        undo_state = ppcurses.memstore.get('undo_state', None)
        if undo_state is not None:
            ppcurses.memstore[ppcurses.memstore['undo_state']].update(cascade=True, reset_position=False, refetch=True)
    ppcurses.memstore['undo_action'] = lambda: None
    ppcurses.memstore['undo_state'] = None
    return state


########################################################################################
#                                 PROJECTPLACE ACTIONS                                 #
########################################################################################


@key('cc')
def create_card(state):
    """ Create a new card """
    change = ppcurses.memstore['carddetailstate'].create_card()
    if change:
        ppcurses.memstore['cardliststate'].update(cascade=True, reset_position=False, refetch=True)
    return state


@key('xx')
def delete_card(state):
    """ Delete a card """
    change = ppcurses.memstore['carddetailstate'].delete_card()
    if change:
        ppcurses.memstore['cardliststate'].update(cascade=True, reset_position=False, refetch=True)
    return state


@key('aa')
def add_co_assignee(state):
    """ Add a co-assignee to a card """
    change = ppcurses.memstore['carddetailstate'].add_co_assignee()
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('ac')
def add_comment(state):
    """ Add a new comment """
    change = ppcurses.memstore['commentsstate'].add_comment()
    if change:
        ppcurses.memstore['commentsstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('ak')
def add_checklist(state):
    """ Add a checklist item """
    change = ppcurses.memstore['carddetailstate'].add_checklist()
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('et')
def change_title(state):
    """ Change the title of the card """
    change = ppcurses.memstore['carddetailstate'].change_title()
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('ed')
def change_description(state):
    """ Change the description of the card """
    change = ppcurses.memstore['carddetailstate'].change_description()
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('eo')
def change_assignee(state):
    """ Change the owner/assignee of the card """
    change = ppcurses.memstore['carddetailstate'].change_assignee()
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('el')
def change_label(state):
    """ Change the label of the card """
    change = ppcurses.memstore['carddetailstate'].change_label()
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('ep')
def change_points(state):
    """ Change the points on a card """
    change = ppcurses.memstore['carddetailstate'].change_points()
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('ek <n>')
def edit_checklist(state):
    """ Edit a checklist item """
    # TODO
    k = ppcurses.memstore['statuswin'].getch()
    change = ppcurses.memstore['carddetailstate'].edit_checklist(chr(k))
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('ec <n>')
def edit_comment(state):
    """ Edit a comment """
    k = ppcurses.memstore['statuswin'].getch()
    change = ppcurses.memstore['commentsstate'].edit_comment(chr(k))
    if change:
        ppcurses.memstore['commentsstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('xa <n>')
def remove_co_assignee(state):
    """ Remove a co-assignee from the card """
    k = ppcurses.memstore['statuswin'].getch()
    change = ppcurses.memstore['carddetailstate'].remove_co_assignee(chr(k))
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('xc <n>')
def delete_comment(state):
    """ Delete a comment """
    k = ppcurses.memstore['statuswin'].getch()
    change = ppcurses.memstore['commentsstate'].delete_comment(chr(k))
    if change:
        ppcurses.memstore['commentsstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('xk <n>')
def delete_checklist(state):
    """ Delete a checklist item """
    k = ppcurses.memstore['statuswin'].getch()
    change = ppcurses.memstore['carddetailstate'].delete_checklist(chr(k))
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('tk <n>')
def toggle_checklist(state):
    """ Toggle a checklist item """
    k = ppcurses.memstore['statuswin'].getch()
    change = ppcurses.memstore['carddetailstate'].toggle_checklist(chr(k))
    if change:
        ppcurses.memstore['carddetailstate'].update(cascade=False, reset_position=False, refetch=True)
    return state


@key('pk <n>')
def checklist_to_card(state):
    """ Convert a checklist item to a card"""
    k = ppcurses.memstore['statuswin'].getch()
    change = ppcurses.memstore['carddetailstate'].checklist_to_card(chr(k))
    if change:
        ppcurses.memstore['cardliststate'].update(cascade=True, reset_position=False, refetch=True)
    return state


@key('mc')
def move_to_column(state):
    """ Move the card to a different column """
    change = ppcurses.memstore['carddetailstate'].move_to_column()
    if change:
        ppcurses.memstore['columnstate'].update(cascade=True, reset_position=False, refetch=True)
    return state


@key('mp')
def move_to_planlet(state):
    """ Move the card to a different activity """
    change = ppcurses.memstore['carddetailstate'].move_to_planlet()
    if change:
        ppcurses.memstore['headerstate'].update(cascade=True, reset_position=True, refetch=True)
    return state


########################################################################################
#                                       NAVIGATION                                     #
########################################################################################


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
            ppcurses.memstore['statuswin'].set(chr(key))
            state = keymap[key](state)
            ppcurses.memstore['statuswin'].unset()
        else:
            ppcurses.memstore['statuswin'].set(chr(key))
            k = ppcurses.memstore['statuswin'].getch()
            state = do(state, k, keymap=keymap[key])
    return state
