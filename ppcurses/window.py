import curses
import logging


logger = logging.getLogger(__name__)


class Window:
    def __init__(self, y, x, endy, endx):
        self.window = curses.newwin(y, x, endy, endx)
        self.window.touchwin()


class ProjectBoardPane(Window):
    def draw(self, state):
        items, _ = state.surrounding()
        logger.info('redrawing ProjectBoardPane')
        self.window.addstr(
                0, 0, ' / '.join([str(items[0]['project_name']), str(items[0]['board_name'])]),
                curses.A_STANDOUT)
        self.window.refresh()
        return self


class SimpleListPane(Window):
    def draw(self, state):
        logger.info('redrawing PlanletPane')
        items, highlight_index = state.surrounding()
        for n, each in enumerate(items):
            self.window.addstr(0, 0, each['name'])
        self.window.refresh()
