import curses
import logging


logger = logging.getLogger(__name__)

INACTIVE_WINDOW = [' ', ' ', ' ', ' ']
ACTIVE_WINDOW = []


class Window:
    def __init__(self, y, x, endy, endx):
        self.window = curses.newwin(y, x, endy, endx)
        self.window.touchwin()

    def refresh(self):
        self.window.refresh()


class ProjectBoardPane(Window):
    def draw(self):
        logger.info('redrawing window of state %s', str(self.state))
        self.window.clear()
        self.window.box()
        items, _ = self.state.surrounding()
        self.window.addstr(
                0, 0, ' / '.join([str(items[0]['project_name']), str(items[0]['board_name'])]),
                curses.A_STANDOUT)
        self.window.refresh()


class SimpleListPane(Window):
    def draw(self):
        logger.info('redrawing window of state %s', str(self.state))
        self.window.clear()
        if self.state.active:
            self.window.border(*ACTIVE_WINDOW)
        else:
            self.window.border(*INACTIVE_WINDOW)

        maxy, maxx = self.window.getmaxyx()
        items, highlight_index = self.state.surrounding(maxy//3)
        for n, each in enumerate(items):
            if n == highlight_index:
                prefix = '> '
            else:
                prefix = '  '
            self.window.addstr(n*2+1, 1, prefix + each['name'])
            self.window.addstr(n*2+2, 1, ''.join(['-']*(maxx-2)))
        self.window.refresh()
