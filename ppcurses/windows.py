import curses


class Window:
    def __init__(self, y, x, endy, endx, state=None):
        self.window = curses.newwin(y, x, endy, endx)
        self.window.touchwin()
        self.state = state

    def refresh(self):
        self.window.refresh()

    def update(self):
        pass

    def getkey(self):
        return self.window.getkey()


class ProjectBoard(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO make a new window to choose project and board on startup, with
        # TODO filtering
        self.project = {'id': 148, 'name': 'meetings'}
        self.board = {'id': 1, 'name': 'board 1'}

    def update(self):
        self.window.addstr(
                0, 0, ' / '.join([self.project['name'], self.board['name']]),
                curses.A_STANDOUT)
        self.refresh()
        return self


class Activities(Window):
    def update(self):
        highlight_index, items = self.state.surrounding
        for n, each in enumerate(items):
            if n == highlight_index:
                mode = curses.A_BOLD
            self.window.addstr(each['name'], mode)
