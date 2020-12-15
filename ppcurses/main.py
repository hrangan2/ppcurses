import curses
import ppcurses
import ppcurses.state
import ppcurses.windows
import ppcurses.data
import ppcurses.keymap
import locale
import logging


logging.basicConfig(filename='ppcurses.log', level=logging.INFO)
logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def interactable(stdscr):
    stdscr.clear()
    curses.curs_set(0)

    # 1 pixel window to listen for keypresses
    statuswin = ppcurses.windows.Status(1, 10, 0, curses.COLS-10)
    ppcurses.memstore['statuswin'] = statuswin

    # Get current user
    ppcurses.data.whoami()

    # Project & Board Header Configuration
    headerstate = ppcurses.state.State('header', ppcurses.data.fileinit)
    headerstate.attach_window(
        ppcurses.windows.ProjectBoard(2, curses.COLS-1, 0, 0),
        )
    ppcurses.memstore['header'] = headerstate

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
    # Card Pane Configuration
    carddetails = ppcurses.state.SingleCard('card details', ppcurses.data.card)
    carddetails.attach_window(
        ppcurses.windows.Pageable(2*(curses.LINES - 2)//3, (curses.COLS-1)//2, (curses.LINES - 2)//3 + 2, 0)
        )

    # Comment List Configuration
    comments = ppcurses.state.Comments('comments', ppcurses.data.comments)
    comments.attach_window(
        ppcurses.windows.Pageable(2*(curses.LINES - 2)//3, (curses.COLS-1)//2, (curses.LINES - 2)//3 + 2, (curses.COLS-1)//2)
        )

    # Link the state objects together
    ppcurses.link(headerstate, planletstate, columnstate, cardstate, carddetails, comments)

    state = planletstate
    state.activate()
    headerstate.update(refetch=True)

    while True:
        key = statuswin.getch()
        state = ppcurses.keymap.do(state, key, allowed_keys=['*'])


def main():
    logger.info('')
    logger.critical('#'*25 + '  Restarting ppcurses  ' + '#'*25)
    logger.info('')
    try:
        curses.wrapper(interactable)
    except ppcurses.errors.GracefulExit:
        pass
    except ppcurses.errors.PPCursesError as err:
        logger.error("Failed due to %s" % repr(err))
