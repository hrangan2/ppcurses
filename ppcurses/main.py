import curses
import ppcurses.state
import ppcurses.window
import ppcurses.api
import ppcurses.keymap
import locale
import logging

# TODO highlight cards assigned to me in the list view


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
    curses.curs_set(0)
    # height_y, width_x, begin_y, begin_x

    # Project & Board Header Configuration
    initstate = ppcurses.state.State(ppcurses.api.staticinit)
    initstate.set_name('header')
    initstate.attach_window(
        ppcurses.window.ProjectBoardPane(2, curses.COLS-1, 0, 0),
        )

    # Planlet List Configuration
    planletstate = ppcurses.state.State(ppcurses.api.planlets)
    planletstate.set_name('planlet')
    planletstate.attach_window(
        ppcurses.window.SimpleListPane((curses.LINES - 2)//3+1, (curses.COLS-1)//3, 1, 0)
        )

    # Column List Configuration
    columnstate = ppcurses.state.State(ppcurses.api.columns)
    columnstate.set_name('column')
    columnstate.attach_window(
        ppcurses.window.SimpleListPane((curses.LINES - 2)//3+1, (curses.COLS-1)//3, 1, (curses.COLS-1)//3)
        )

    # Card List Configuration
    cardstate = ppcurses.state.State(ppcurses.api.cards)
    cardstate.set_name('card')
    cardstate.attach_window(
        ppcurses.window.SimpleListPane((curses.LINES - 2)//3+1, (curses.COLS-1)//3, 1, 2*(curses.COLS-1)//3)
        )
    ppcurses.state.link(initstate, planletstate, columnstate, cardstate)

    # Card Pane Configuration
    carddetails = ppcurses.state.SingleCard(ppcurses.model.Card)
    carddetails.attach_window(
        ppcurses.window.CardPane(2*(curses.LINES - 2)//3, (curses.COLS-1)//2, (curses.LINES - 2)//3 + 2, 0)
        )

    # Link the state objects together
    ppcurses.state.link(initstate, planletstate, columnstate, cardstate, carddetails)

    # Comment List Configuration

    # 1 pixel window to listen for keypresses
    keylistener = curses.newwin(0, curses.COLS-1, 0, curses.COLS-1)

    state = planletstate
    state.active = True

    initstate.update()

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
