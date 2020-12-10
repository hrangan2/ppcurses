import curses
import ppcurses
import ppcurses.state
import ppcurses.window
import ppcurses.api
import locale
import logging


logging.basicConfig(filename='ppcurses.log', level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def interactable(stdscr):
    logger.critical('\n' + '#'*25 + '  Restarting ppcurses  ' + '#'*25 + '\n')
    stdscr.clear()
    # height_y, width_x, begin_y, begin_x

    initstate = ppcurses.state.State(ppcurses.api.staticinit)
    initstate.attach_window(
        ppcurses.window.ProjectBoardPane(1, curses.COLS-1, 0, 0),
        )

    planletstate = ppcurses.state.State(ppcurses.api.planlets, lambda x: [x['board_id']])
    planletstate.attach_window(
        ppcurses.window.SimpleListPane(14, (curses.COLS-1)//3 - 1, 3, 0)
        )

    columnstate = ppcurses.state.State(ppcurses.api.columns)
    columnstate.attach_window(
        ppcurses.window.SimpleListPane(14, 2*(curses.COLS-1)//3 - 1, 3, (curses.COLS-1)//3)
        )

    cardstate = ppcurses.state.State(ppcurses.api.cards)
    cardstate.attach_window(
        ppcurses.window.SimpleListPane(14, curses.COLS-1, 3, 2*(curses.COLS-1)//3)
        )
    ppcurses.state.link(initstate, planletstate)

    initstate.update()
    keylistener = curses.newwin(0, curses.COLS-1, 0, curses.COLS-1)
    while True:
        if keylistener.getkey().lower() == 'q':
            return


def main():
    curses.wrapper(interactable)
