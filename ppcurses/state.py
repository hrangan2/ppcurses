import logging

logger = logging.getLogger(__name__)


class Zero:
    def __init__(self, text):
        self.text = text

    def __getitem__(self, key):
        return self.text if key == 'name' else None


class State:
    zerostate = [Zero('No items to show')]

    def __init__(self, updatef, prev_argf=lambda x: [x['id']], name=None):
        self.active = False
        self._name = name
        self.updatef = updatef
        self.prev_argf = prev_argf
        self.data = self.zerostate
        self.current_id = self.data[0]['id']

    def __repr__(self):
        if hasattr(self, '_name') and self._name:
            return '<namedstate: %s>' % self._name
        else:
            return super().__repr__()

    def set_name(self, name):
        self._name = name

    def attach_window(self, window):
        self.window = window
        self.window.state = self

    def update(self):
        if hasattr(self, 'pstate'):
            prev_args = self.prev_argf(self.pstate.current_item)
            if prev_args and prev_args == ([None] * len(prev_args)):
                self.data = self.zerostate
            else:
                self.data = self.updatef(*prev_args) or self.zerostate
        else:
            self.data = self.updatef() or self.zerostate
        self.ids = [each['id'] for each in self.data]
        if hasattr(self, 'window'):
            self.window.draw()
        if hasattr(self, 'nstate'):
            logger.info('updating linked state %s of %s', self.nstate, self)
            self.nstate.update()

    def prev(self):
        if self.index == 0:
            return

        self.current_id = self.data[self.index - 1]['id']
        self.window.draw()

    def next(self):
        if len(self.data) == 1:
            return
        if self.index == len(self.data) - 1:
            return

        self.current_id = self.data[self.index + 1]['id']
        self.window.draw()

    @property
    def current_item(self):
        return self.data[self.index]

    def surrounding(self, n=4):
        before_count = n//2
        after_count = n//2
        if n % 2:
            after_count += 1
        items = []
        if after_count + self.index >= len(self.data):
            for x in range(after_count):
                try:
                    items.append(self.data[self.index + x + 1])
                    # print('>', items)
                except IndexError:
                    before_count += 1
                    after_count -= 1
            items.insert(0, self.current_item)
            # print('-', items)

            for x in range(1, before_count+1, 1):
                if (self.index - x) < 0:
                    after_count += 1
                    before_count -= 1
                else:
                    items.insert(0, self.data[self.index - x])
                    # print('<', items)
        else:
            for x in range(before_count, 0, -1):
                if (self.index - x) < 0:
                    after_count += 1
                    before_count -= 1
                else:
                    items.append(self.data[self.index - x])
            items.append(self.current_item)

            for x in range(after_count):
                try:
                    items.append(self.data[self.index + x + 1])
                except IndexError:
                    before_count += 1
                    after_count -= 1
        highlight_index = [each['id'] for each in items].index(self.current_id)
        return items, highlight_index

    @property
    def index(self):
        try:
            return self.ids.index(self.current_id)
        except ValueError:
            self.current_id = self.data[0]['id']
            return 0

    def resetzero(self):
        self.current_id = self.data[0]['id']


def link(*states):
    """ You need to pass a list of states to this function before they can work """
    logger.info('linking %s states', len(states))
    for n, each in enumerate(states):
        if n:
            each.pstate = states[n-1]
        try:
            each.nstate = states[n+1]
        except IndexError:
            pass


class CommentPad:
    pass


class CardPane:
    pass
