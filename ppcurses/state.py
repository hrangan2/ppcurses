import logging
import textwrap

logger = logging.getLogger(__name__)


class Zero:
    def __init__(self, text):
        self.text = text

    def __getitem__(self, key):
        return self.text if key == 'name' else None

    def __getattr__(self, key):
        return super().__getattr__(self, 'text') if key == 'name' else None


class State:
    zerostate = [Zero('No items to show')]

    def __init__(self, updatef, name=None):
        self.active = False
        self.name = name
        self.updatef = updatef
        self.data = self.zerostate
        self.current_id = self.data[0]['id']

    def __repr__(self):
        if hasattr(self, 'name') and self.name:
            return '<namedstate: %s>' % self.name
        else:
            return super().__repr__()

    def set_name(self, name):
        self.name = name

    def attach_window(self, window):
        self.window = window
        self.window.state = self

    def update(self):
        if hasattr(self, 'pstate'):
            prev_args = self.pstate.current_item
            if prev_args['id'] is None:
                self.data = self.zerostate
            else:
                self.data = self.updatef(prev_args) or self.zerostate
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
        if hasattr(self, 'nstate'):
            self.nstate.update()

    def next(self):
        if len(self.data) == 1:
            return
        if self.index == len(self.data) - 1:
            return

        self.current_id = self.data[self.index + 1]['id']
        self.window.draw()
        if hasattr(self, 'nstate'):
            self.nstate.update()

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

        scroll_up = True
        scroll_down = True

        if (self.index - highlight_index) <= 0:
            scroll_up = False
        if len(self.data) <= n:
            scroll_down = False
        if (self.index + (n+highlight_index)) > len(self.data):
            scroll_down = False

        return items, highlight_index, scroll_up, scroll_down

    @property
    def index(self):
        try:
            return self.ids.index(self.current_id)
        except ValueError:
            self.current_id = self.data[0]['id']
            return 0


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


class SingleCard:
    zerostate = Zero('No card selected')

    def __init__(self, model):
        self.active = False
        self.model = model
        self.card = self.zerostate
        self.index = 0

    def attach_window(self, window):
        self.window = window
        self.window.state = self

    def update(self):
        self.index = 0
        prev_args = self.pstate.current_item
        if prev_args['id'] is None:
            self.card = self.zerostate
        else:
            self.card = self.model(prev_args) or self.zerostate

        self.lines_of_text = self.generate_lines_of_text()

        if hasattr(self, 'window'):
            self.window.draw()

        if hasattr(self, 'nstate'):
            logger.info('updating linked state %s of %s', self.nstate, self)
            self.nstate.update()

    def generate_lines_of_text(self):
        if self.card.id is None:
            return [self.card.text]

        contents = []
        contents.extend(textwrap.wrap(self.card.title, width=self.window.maxx))
        contents.append(' ')
        if self.card.description:
            contents.append('Description:')
            for line in self.card.description.split('\n'):
                contents.extend(textwrap.wrap(line, width=self.window.maxx-5))
            contents.append(' ')
        contents.append('Assignee: %s' % str(self.card.assignee['name'] if self.card.assignee else None))
        contributors = ','.join([each['name'] for each in self.card.contributors]) or str(None)
        contents.append('Co-Assignees: %s' % contributors)
        contents.append(' ')
        if self.card.label:
            contents.append('Label: %s' % str(self.card.label['name'] if self.card.label else None))
        if self.card.estimate:
            contents.append('Points: %s' % str(self.card.estimate))
        if self.card.tags:
            tags = ','.join([each['name'] for each in self.card.tags]) or str(None)
            contents.append('Tags: %s' % str(tags))

        if self.card.checklist:
            contents.append(' ')
            contents.append('Checklist:')
            for each in self.card.checklist:
                if each['done']:
                    contents.append('[X] %s' % each['title'])
                else:
                    contents.append('[ ] %s' % each['title'])
        return contents

    @property
    def lines_needed(self):
        return len(self.lines_of_text)

    def surrounding(self):
        if self.lines_needed > self.window.maxy-2:
            if self.index == 0:
                scroll_up = False
            else:
                scroll_up = True

            if (self.lines_needed - self.index) < self.window.maxy-1:
                scroll_down = False
            else:
                scroll_down = True

            return self.lines_of_text[self.index: self.index + self.window.maxy-2], scroll_up, scroll_down
        else:
            scroll_up = False
            scroll_down = False
            return self.lines_of_text, scroll_up, scroll_down

    def prev(self):
        if self.index == 0:
            return
        self.index -= (self.window.maxy//2)
        self.index = max(self.index, 0)
        self.window.draw()

    def next(self):
        if (self.lines_needed - self.index) < self.window.maxy-1:
            return
        self.index += (self.window.maxy//2)
        self.window.draw()


class CommentPad:
    zerostate = Zero('No comments to show')

    def __init__(self, model):
        self.active = False
        self.model = model
        self.comments = self.zerostate

    def attach_window(self, window):
        self.window = window
        self.window.state = self

    def update(self):
        prev_args = self.pstate.current_item
        if prev_args['id'] is None:
            self.card = [self.zerostate]
        else:
            self.card = self.model(prev_args) or self.zerostate

        if hasattr(self, 'window'):
            self.window.draw()
        if hasattr(self, 'nstate'):
            logger.info('updating linked state %s of %s', self.nstate, self)
            self.nstate.update()

    def prev(self):
        pass

    def next(self):
        pass
