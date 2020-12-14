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

    keylistener = curses.newwin(0, curses.COLS-1, 0, curses.COLS-1)
    keylistener.keypad(True)
    state = projects

    while True:
        key = keylistener.getch()
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
                'r',
                'q'])
        except ppcurses.errors.GracefulExit:
            # Remove any characters printed by these windows in the gaps
            # between existing windows
            projects.window.window.clear()
            boards.window.window.clear()
            projects.window.window.refresh()
            boards.window.window.refresh()
            if ppcurses.dbstore['project_id'] is None or ppcurses.dbstore['board_id'] is None:
                exit()
            else:
                break
    win.clear()
    win.refresh()
