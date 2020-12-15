import curses
import curses.ascii
import logging
import ppcurses
import ppcurses.state
import ppcurses.errors

logger = logging.getLogger(__name__)


def select_project_board():
    win = curses.newwin(curses.LINES-1, curses.COLS-1, 0, 0)
    win.clear()
    win.addstr(2, 6, 'Choose a project and a board:')
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
                projects.window.clear()
                boards.window.clear()
                projects.window.refresh()
                boards.window.refresh()
                break
        try:
            state = ppcurses.keymap.do(state, key, allowed_keys=[
                'h', chr(curses.KEY_LEFT),
                'j', chr(curses.KEY_DOWN),
                'k', chr(curses.KEY_UP),
                'l', chr(curses.KEY_RIGHT),
                'r',
                'q'])
        except ppcurses.errors.GracefulExit:
            # Remove any characters printed by these windows in the gaps
            # between existing windows
            projects.window.clear()
            boards.window.clear()
            projects.window.refresh()
            boards.window.refresh()
            if ppcurses.dbstore['project_id'] is None or ppcurses.dbstore['board_id'] is None:
                exit()
            else:
                break
    win.clear()
    win.refresh()


def select_one(name, updater):
    state = ppcurses.state.State('%ss' % name, updater)
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
                state.window.clear()
                state.window.refresh()
                break
        try:
            state = ppcurses.keymap.do(state, key, allowed_keys=[
                'h', chr(curses.KEY_LEFT),
                'j', chr(curses.KEY_DOWN),
                'k', chr(curses.KEY_UP),
                'l', chr(curses.KEY_RIGHT),
                'q'])
        except ppcurses.errors.GracefulExit:
            # Remove any characters printed by these windows in the gaps
            # between existing windows
            state.window.clear()
            state.window.refresh()
            break
    ppcurses.memstore['header'].update()
    return selection
