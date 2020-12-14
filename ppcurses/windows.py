import curses
import textwrap
import logging


logger = logging.getLogger(__name__)

INACTIVE_WINDOW = [' ', ' ', ' ', ' ']
ACTIVE_WINDOW = []


class Window:
    def __init__(self, nlines, ncols, begin_y, begin_x):
        self.window = curses.newwin(nlines, ncols, begin_y, begin_x)
        self.window.touchwin()
        self.maxy, self.maxx = self.window.getmaxyx()
        self.window.keypad(True)


class ProjectBoard(Window):
    def draw(self):
        logger.info('redrawing window of state %s', str(self.state))
        self.window.clear()
        items, _, _, _ = self.state.surrounding()
        title = ' %s - %s ' % (items[0]['project_name'].upper(), items[0]['board_name'].upper())
        self.window.addstr(0, 5, title, curses.A_STANDOUT)
        self.window.refresh()


class SimpleList(Window):
    def draw(self):
        logger.info('redrawing window of state %s', str(self.state))
        self.window.clear()
        if self.state._active:
            self.window.border(*ACTIVE_WINDOW)
        else:
            self.window.border(*INACTIVE_WINDOW)
        self.window.addstr(0, 2, self.state.name)

        items, highlight_index, scroll_up, scroll_down = self.state.surrounding(self.maxy//2-2)

        if scroll_up:
            self.window.addch(1, self.maxx-3, curses.ACS_UARROW)
        if scroll_down:
            self.window.addch(self.maxy-2, self.maxx-3, curses.ACS_DARROW)

        for n, each in enumerate(items):
            if n == highlight_index:
                prefix = '> '
            else:
                prefix = '  '
            self.window.addstr(n*2+1, 1, prefix + textwrap.shorten(each['name'], width=self.maxx-7, placeholder='...'))
            self.window.addstr(n*2+2, 1, ''.join(['-']*(self.maxx-5)))
        self.window.refresh()


class Pageable(Window):
    def draw(self):
        logger.info('redrawing window of state %s', self.state.name)
        self.window.clear()
        if self.state._active:
            self.window.border(*ACTIVE_WINDOW)
        else:
            self.window.border(*INACTIVE_WINDOW)
        self.window.addstr(0, 2, self.state.name)
        lines, scroll_up, scroll_down = self.state.surrounding()

        if scroll_up:
            self.window.addch(1, self.maxx-3, curses.ACS_UARROW)
        if scroll_down:
            self.window.addch(self.maxy-2, self.maxx-3, curses.ACS_DARROW)

        for n, line in enumerate(lines):
            self.window.addstr(n+1, 1, textwrap.shorten(line, width=self.maxx-3))
        self.window.refresh()


class Status(Window):
    def set(self, text):
        self.window.clear()
        self.window.addstr(0, 0, textwrap.shorten(text, width=self.maxx-1, placeholder='#'))
        self.window.refresh()

    def unset(self):
        self.window.clear()
        self.window.refresh()

    def getch(self):
        return self.window.getch()
