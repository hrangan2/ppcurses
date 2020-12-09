import curses
import locale
from ppcurses import windows


locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()


def interactable(stdscr):
    stdscr.clear()
    views = [
            windows.ProjectBoard(1, curses.COLS-1, 0, 0),
            windows.Activities(2, (curses.COLS-1)//3 - 1, 1, 0)
            ]
    active_windows = [each.update() for each in views]
    active_index = 0
    keylistener = curses.newwin(0, curses.COLS-1, 0, curses.COLS-1)
    while True:
        if keylistener.getkey().lower() == 'q':
            return


def main():
    curses.wrapper(interactable)
