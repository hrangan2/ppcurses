import curses
import ppcurses.state
import ppcurses.window
import ppcurses.api
import ppcurses.keymap
import locale
import logging


logging.basicConfig(filename='ppcurses.log', level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def interactable(stdscr):
    logger.info('')
    logger.info('#'*25 + '  Restarting ppcurses  ' + '#'*25)
    logger.info('')
    ppcurses.api.quickfail_dns()
    stdscr.clear()
    # height_y, width_x, begin_y, begin_x

    initstate = ppcurses.state.State(ppcurses.api.staticinit)
    initstate.set_name('header')
    initstate.attach_window(
        ppcurses.window.ProjectBoardPane(1, curses.COLS-1, 0, 0),
        )

    planletstate = ppcurses.state.State(ppcurses.api.planlets, lambda x: [x['board_id']])
    planletstate.set_name('planlets')
    planletstate.attach_window(
        ppcurses.window.SimpleListPane((curses.LINES - 2)//2, (curses.COLS-1)//3, 2, 0)
        )

    columnstate = ppcurses.state.State(ppcurses.api.columns)
    columnstate.set_name('columns')
    columnstate.attach_window(
        ppcurses.window.SimpleListPane((curses.LINES - 2)//2, 2*(curses.COLS-1)//3, 2, (curses.COLS-1)//3)
        )

    cardstate = ppcurses.state.State(ppcurses.api.cards)
    cardstate.set_name('cards')
    cardstate.attach_window(
        ppcurses.window.SimpleListPane((curses.LINES - 2)//2, curses.COLS-1, 2, 2*(curses.COLS-1)//3)
        )
    ppcurses.state.link(initstate, planletstate)

    initstate.update()
    keylistener = curses.newwin(0, curses.COLS-1, 0, curses.COLS-1)
    state = planletstate
    while True:
        key = keylistener.getkey()
        state = ppcurses.keymap.do(state, key)


def main():
    try:
        curses.wrapper(interactable)
    except ppcurses.errors.GracefulExit:
        pass
    except ppcurses.errors.PPCursesError as err:
        logger.error("Failed due to %s" % repr(err))
