import curses
import ppcurses.state
import ppcurses.windows
import ppcurses.data
import ppcurses.keymap
import locale
import logging

# TODO highlight cards assigned to me in the list view


logging.basicConfig(filename='ppcurses.log', level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def interactable(stdscr):
    stdscr.clear()
    ppcurses.data.network_quickfail()
    curses.curs_set(0)
    # height_y, width_x, begin_y, begin_x

    # Project & Board Header Configuration
    initstate = ppcurses.state.State('header', ppcurses.data.staticinit)
    initstate.attach_window(
        ppcurses.windows.ProjectBoard(2, curses.COLS-1, 0, 0),
        )

    # Planlet List Configuration
    planletstate = ppcurses.state.State('planlet', ppcurses.data.planlets)
    planletstate.attach_window(
        ppcurses.windows.SimpleList((curses.LINES - 2)//3+1, (curses.COLS-1)//3, 1, 0)
        )

    # Column List Configuration
    columnstate = ppcurses.state.State('column', ppcurses.data.columns)
    columnstate.attach_window(
        ppcurses.windows.SimpleList((curses.LINES - 2)//3+1, (curses.COLS-1)//3, 1, (curses.COLS-1)//3)
        )

    # Card List Configuration
    cardstate = ppcurses.state.State('card', ppcurses.data.cards)
    cardstate.attach_window(
        ppcurses.windows.SimpleList((curses.LINES - 2)//3+1, (curses.COLS-1)//3, 1, 2*(curses.COLS-1)//3)
        )
    ppcurses.state.link(initstate, planletstate, columnstate, cardstate)

    # Card Pane Configuration
    carddetails = ppcurses.state.SingleCard('card details', ppcurses.data.Card)
    carddetails.attach_window(
        ppcurses.windows.Pageable(2*(curses.LINES - 2)//3, (curses.COLS-1)//2, (curses.LINES - 2)//3 + 2, 0)
        )

    # Comment List Configuration
    comments = ppcurses.state.Comments('comments', ppcurses.data.comments)
    comments.attach_window(
        ppcurses.windows.Pageable(2*(curses.LINES - 2)//3, (curses.COLS-1)//2, (curses.LINES - 2)//3 + 2, (curses.COLS-1)//2)
        )

    # Link the state objects together
    ppcurses.state.link(initstate, planletstate, columnstate, cardstate, carddetails, comments)

    # 1 pixel window to listen for keypresses
    keylistener = curses.newwin(0, curses.COLS-1, 0, curses.COLS-1)

    state = planletstate
    state.active = True

    initstate.update()

    while True:
        key = keylistener.getkey()
        state = ppcurses.keymap.do(state, key, allowed_keys=['*'])


def main():
    logger.info('')
    logger.info('#'*25 + '  Restarting ppcurses  ' + '#'*25)
    logger.info('')
    try:
        curses.wrapper(interactable)
    except ppcurses.errors.GracefulExit:
        pass
    except ppcurses.errors.PPCursesError as err:
        logger.error("Failed due to %s" % repr(err))
