class State:
    zerostate = {'id': None, 'name': 'No items to show'}

    def __init__(self, updatef, prev_argf=lambda x: [x['id']], id=None):
        self.id = id
        self.updatef = updatef
        self.prev_argf = prev_argf
        self.update()
        if not self.data:
            self.data = [self.zerostate]

        self.current_id = self.data[0]['id']

    def __repr__(self):
        if self.id is not None:
            return 'StateObj: %s' % str(self.id)
        else:
            return super().__repr__()

    def update(self):
        if hasattr(self, 'pstate'):
            self.data = self.updatef(*self.prev_argf(self.pstate.current_item))
        else:
            self.data = self.updatef()
        self.ids = [each['id'] for each in self.data]
        if hasattr(self, 'nstate'):
            self.nstate.update()

    def prev(self):
        if self.index == 0:
            return

        self.current_id = self.data[self.index - 1]['id']

    def next(self):
        if len(self.data) == 1:
            return
        if self.index == len(self.data) - 1:
            return

        self.current_id = self.data[self.index + 1]['id']

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
    for n, each in enumerate(states):
        if n:
            each.pstate = states[n-1]

        try:
            each.nstate = states[n+1]
        except IndexError:
            pass
