import curses
import logging
import ppcurses
import ppcurses.state
import ppcurses.errors

logger = logging.getLogger(__name__)


def select_project_board():
    projects = ppcurses.state.State('project', ppcurses.data.projects)
    projects.attach_window(
        ppcurses.windows.SimpleList(curses.LINES - 1, (curses.COLS-1)//2, 1, 0)
        )

    # Column List Configuration
    boards = ppcurses.state.State('board', ppcurses.data.boards)
    boards.attach_window(
        ppcurses.windows.SimpleList(curses.LINES - 1, (curses.COLS-1)//2, 1, (curses.COLS-1)//2)
        )

    ppcurses.link(projects, boards)

    projects.update()

    keylistener = curses.newwin(0, curses.COLS-1, 0, curses.COLS-1)
    state = projects

    while True:
        key = keylistener.getkey()
        if key == '\n':
            if projects.current_item['id'] is not None and boards.current_item['id']:
                ppcurses.dbstore['project_id'] = projects.current_item['id']
                ppcurses.dbstore['project_name'] = projects.current_item['name']
                ppcurses.dbstore['board_id'] = boards.current_item['id']
                ppcurses.dbstore['board_name'] = boards.current_item['name']
                break
        try:
            state = ppcurses.keymap.do(state, key, allowed_keys=['h', 'j', 'k', 'l', 'q'])
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
