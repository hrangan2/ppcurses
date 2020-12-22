import curses
import re
import pyperclip
import string
import textwrap
import curses.ascii
import logging
import ppcurses
import ppcurses.state
import ppcurses.errors
import ppcurses.data

logger = logging.getLogger(__name__)


def select_project_board():
    win = curses.newwin(curses.LINES-1, curses.COLS-1, 0, 0)
    win.clear()
    win.addstr(2, 6, 'Choose a project and a board (press ESC to quit):')
    win.refresh()
    border = 5

    projects = ppcurses.state.State('project', ppcurses.data.projects)
    projects.attach_window(
        ppcurses.windows.SimpleList(curses.LINES - 1-(2*border), (curses.COLS-1)//2-border, 1+border, 0+border)
        )

    boards = ppcurses.state.State('board', ppcurses.data.boards)
    boards.attach_window(
        ppcurses.windows.SimpleList(curses.LINES - 1-(2*border), (curses.COLS-1)//2-border, 1+border, (curses.COLS-1)//2)
        )

    ppcurses.link(projects, boards)

    projects.activate()
    projects.update()

    state = projects

    while True:
        key = ppcurses.memstore['statuswin'].getch()
        if key == curses.ascii.NL:
            if projects.current_item['id'] is not None and boards.current_item['id']:
                ppcurses.dbstore.set_forever('project_id', projects.current_item['id'])
                ppcurses.dbstore.set_forever('project_name', projects.current_item['name'])
                ppcurses.dbstore.set_forever('board_id', boards.current_item['id'])
                ppcurses.dbstore.set_forever('board_name', boards.current_item['name'])
                break
        try:
            state = ppcurses.keymap.do(state, key, allowed_keys=[
                'h', chr(curses.KEY_LEFT),
                'j', chr(curses.KEY_DOWN),
                'k', chr(curses.KEY_UP),
                'l', chr(curses.KEY_RIGHT),
                'g', 'G',
                'r',
                '/',
                chr(curses.ascii.ESC)])
        except ppcurses.errors.GracefulExit:
            # Remove any characters printed by these windows in the gaps
            # between existing windows
            if ppcurses.dbstore['project_id'] is None or ppcurses.dbstore['board_id'] is None:
                raise ppcurses.errors.ApplicationExit
            else:
                break
    projects.window.clear()
    boards.window.clear()
    projects.window.refresh()
    boards.window.refresh()
    win.clear()
    win.refresh()


def select_one(name, updater):
    state = ppcurses.state.State('%s' % name, updater)
    state.attach_window(
        ppcurses.windows.SimpleList(2*(curses.LINES - 1)//4, (curses.COLS-1)//2, (curses.LINES - 1)//4, (curses.COLS-1)//4)
        )
    state.activate()
    state.update()

    selection = None
    while True:
        key = ppcurses.memstore['statuswin'].getch()
        if key == curses.ascii.NL:
            if state.current_item['id'] is not None:
                selection = state.current_item
                break
        try:
            state = ppcurses.keymap.do(state, key, allowed_keys=[
                'h', chr(curses.KEY_LEFT),
                'j', chr(curses.KEY_DOWN),
                'k', chr(curses.KEY_UP),
                'l', chr(curses.KEY_RIGHT),
                chr(curses.ascii.ESC), 'r', 'g', 'G', '/'])
        except ppcurses.errors.GracefulExit:
            # Remove any characters printed by these windows in the gaps
            # between existing windows
            break
    state.window.clear()
    state.window.refresh()
    ppcurses.memstore['headerstate'].update()
    return selection


def decode_atref(text, known_atrefs={}):
    board_members = known_atrefs
    remote_board_members = {each['id']: each['name'] for each in ppcurses.data.get_board_members()}
    board_members.update(remote_board_members)

    def board_member_replacer(matchobj):
        return '@' + board_members[int(matchobj.groups()[0])]

    return re.sub(r'@\[([0-9]+)\]', board_member_replacer, text)


def remove_atref(text):
    regex = r'.*(@\[[0-9]+\]$)'
    match = re.match(regex, text)
    if match is not None:
        return len(match.groups()[0])
    else:
        return None


def strip_removed_members(text, known_atrefs={}):
    board_members = known_atrefs
    for each in ppcurses.data.get_board_members():
        try:
            board_members.pop(each['id'])
        except KeyError:
            pass

    def board_member_replacer(matchobj):
        try:
            return '@' + board_members[int(matchobj.groups()[0])]
        except KeyError:
            return '@[%s]' % int(matchobj.groups()[0])

    return re.sub(r'@\[([0-9]+)\]', board_member_replacer, text)


def textbox(name, text='', newlines=False, encoded=False, encoder_kwargs={}):
    original_text = text

    if encoded:
        text = strip_removed_members(text, **encoder_kwargs)

    def draw_text(window, text):
        window.clear()
        window.border(*ppcurses.windows.ACTIVE_WINDOW)
        window.addstr(0, 2, name)
        if newlines:
            window.addstr(maxy-2, 2, 'ctrl-s to confirm, esc to cancel')
        else:
            window.addstr(maxy-2, 2, 'enter to confirm, esc to cancel')

        if not text:
            # This is to move the cursor to this location
            window.addstr(2, 3, '')
        lines = []
        raw_text = decode_atref(text, **encoder_kwargs) if encoded else text
        for line in raw_text.split('\n'):
            wrapped = textwrap.wrap(line, width=maxx-6, drop_whitespace=False, replace_whitespace=False)
            if not wrapped:
                lines.append('')
            else:
                lines.extend(wrapped)
        for n, line in enumerate(lines[-maxy+5:]):
            window.addstr(n+2, 3, line)
        window.refresh()

    window = curses.newwin(2*(curses.LINES - 1)//4, 6*(curses.COLS-1)//8, (curses.LINES - 1)//4, (curses.COLS-1)//8)
    maxy, maxx = window.getmaxyx()
    window.touchwin()
    window.keypad(True)

    while True:
        curses.curs_set(1)  # Child windows sometimes unset the cursor
        draw_text(window, text)
        key = ppcurses.memstore['statuswin'].window.getch()

        if (key == -1) or (key == curses.KEY_RESIZE):
            continue
        elif key == curses.ascii.ctrl(ord('s')):
            if newlines:
                break
        elif key == curses.ascii.ESC:
            text = None
            break
        elif key == curses.ascii.ctrl(ord('v')):
            text += pyperclip.paste()
        elif key == curses.ascii.ctrl(ord('w')):
            if text.endswith('\n'):
                text = text[:-1]
            elif text.endswith(' '):
                text = text.rstrip()
            elif text.endswith(']'):
                removal_chars = remove_atref(text)
                if removal_chars is not None:
                    text = text[:-removal_chars]
                else:
                    text = text[:-1]
            else:
                chars_to_remove = len(text.split(' ')[-1].split('\n')[-1])
                text = text[:-chars_to_remove]
                if text.endswith(' '):
                    text = text.rstrip()
        elif key == curses.ascii.NL:
            if newlines:
                text += '\n'
            else:
                break
        elif key == curses.ascii.DEL:
            if text.endswith(']'):
                removal_chars = remove_atref(text)
                if removal_chars is not None:
                    text = text[:-removal_chars]
                else:
                    text = text[:-1]
            else:
                text = text[:-1]
        elif key == ord('@'):
            if encoded:
                member = select_one('board members', ppcurses.data.get_board_members)
                if member is not None:
                    text += '@[%s]' % member['id']
            else:
                text += chr(key)
        elif chr(key) in string.printable+' ':
            text += chr(key)

    window.clear()
    window.refresh()
    ppcurses.memstore['headerstate'].update()
    curses.curs_set(0)
    if (not text) or (text == original_text):
        return None, None
    if encoded:
        return decode_atref(text, **encoder_kwargs), text
    else:
        return text, None


def filter(state):
    window = curses.newwin(4, 4*(curses.COLS-1)//8, 3*(curses.LINES - 1)//4-4, 2*(curses.COLS-1)//8)
    window.border()
    maxy, maxx = window.getmaxyx()
    window.touchwin()
    window.keypad(True)
    curses.curs_set(1)
    prev_filter_text = state.filter_text

    while True:
        state.update()
        window.clear()
        window.border(*ppcurses.windows.ACTIVE_WINDOW)
        window.addstr(maxy-2, 2, 'enter to confirm, esc to cancel')
        window.addstr(1, 2, state.filter_text)
        window.refresh()
        key = ppcurses.memstore['statuswin'].window.getch()
        if (key == -1) or (key == curses.KEY_RESIZE):
            continue
        elif key == curses.ascii.DEL:
            state.filter_text = state.filter_text[:-1]
        elif key == curses.ascii.NL:
            if state.current_item['id'] is None:
                state.filter_text = ''
            break
        elif key == curses.ascii.ESC:
            state.filter_text = prev_filter_text
            break
        elif chr(key) in string.printable+' ':
            state.filter_text += chr(key)

    window.clear()
    window.refresh()
    state.update()
    curses.curs_set(0)
    return state
