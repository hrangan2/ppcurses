import logging
import ppcurses
import ppcurses.hover
import textwrap

logger = logging.getLogger(__name__)


class Zero:
    def __init__(self, name):
        self.name = name
        self.text = name

    def __getitem__(self, key):
        return self.name if key == 'name' else None

    def __getattr__(self, key):
        return None


class State:
    zerostate = [Zero('No items to show')]

    def __init__(self, name, updater):
        self.name = name
        self._active = False
        self.updater = updater
        self.data = self.zerostate
        self.current_id = self.data[0]['id']

    def __repr__(self):
        if hasattr(self, 'name') and self.name:
            return '<namedstate: %s>' % self.name
        else:
            return super().__repr__()

    def activate(self):
        self._active = True

    def deactivate(self):
        self._active = False

    def attach_window(self, window):
        self.window = window
        self.window.state = self

    def update(self, cascade=True, reset_position=False, refetch=False):
        if hasattr(self, 'pstate'):
            prev_args = self.pstate.current_item
            if prev_args['id'] is None:
                self.data = self.zerostate
            else:
                self.data = self.updater(prev_args, refetch=refetch) or self.zerostate
        else:
            self.data = self.updater(refetch=refetch) or self.zerostate
        self.ids = [each['id'] for each in self.data]
        if reset_position:
            self.current_id = self.data[0]['id']
        if hasattr(self, 'window'):
            self.window.draw()
        if cascade and hasattr(self, 'nstate'):
            logger.debug('updating linked state %s of %s', self.nstate, self)
            self.nstate.update(reset_position=reset_position, refetch=refetch)

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
        if (self.index + 2+(n-highlight_index)) > len(self.data):
            scroll_down = False

        return items, highlight_index, scroll_up, scroll_down

    @property
    def index(self):
        try:
            return self.ids.index(self.current_id)
        except ValueError:
            self.current_id = self.data[0]['id']
            return 0


class Pager:
    def __init__(self, name, updater):
        self.name = name
        self._active = False
        self.updater = updater
        self.data = self.zerostate
        self.index = 0

    def activate(self):
        self._active = True

    def deactivate(self):
        self._active = False

    @property
    def current_item(self):
        return {'id': self.data.id, 'card_id': self.data.id}

    def attach_window(self, window):
        self.window = window
        self.window.state = self

    def update(self, cascade=True, reset_position=False, refetch=False):
        prev_args = self.pstate.current_item
        if prev_args['id'] is None:
            self.data = self.zerostate
        else:
            self.data = self.updater(prev_args, refetch=refetch) or self.zerostate
        if reset_position:
            self.index = 0
        self.lines_of_text = self.generate_lines_of_text()
        if hasattr(self, 'window'):
            self.window.draw()

        if cascade and hasattr(self, 'nstate'):
            logger.debug('updating linked state %s of %s', self.nstate, self)
            self.nstate.update(reset_position=reset_position, refetch=refetch)

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


class SingleCard(Pager):
    zerostate = Zero('No card selected')

    def update(self, cascade=True, reset_position=False, refetch=False):
        super().update(cascade=cascade, reset_position=reset_position, refetch=refetch)
        ppcurses.memstore['card_id'] = self.data.id

    def generate_lines_of_text(self):
        if self.data.id is None:
            return [self.data.text]

        contents = []
        contents.extend(textwrap.wrap(self.data.title, width=self.window.maxx-3))
        contents.append(' ')
        if self.data.description:
            contents.append('Description:')
            for line in self.data.description.split('\n'):
                contents.extend(textwrap.wrap(line, width=self.window.maxx-3))
            contents.append(' ')
        contents.append('Assignee: %s' % str(self.data.assignee['name'] if self.data.assignee else None))
        contributors = ','.join([each['name'] for each in self.data.contributors]) or str(None)
        contents.append('Co-Assignees: %s' % contributors)
        contents.append(' ')
        if self.data.label:
            contents.append('Label: %s' % str(self.data.label['name'] if self.data.label else None))
        if self.data.estimate:
            contents.append('Points: %s' % str(self.data.estimate))

        if self.data.checklist:
            contents.append(' ')
            contents.append('Checklist:')
            for n, each in enumerate(self.data.checklist):
                if each['done']:
                    contents.append('%s. [X] %s' % (n, each['title']))
                else:
                    contents.append('%s. [ ] %s' % (n, each['title']))
        return contents

    def delete_checklist(self, index):
        if self.data.id is None:
            return False
        try:
            checklist = self.data.checklist[index]
        except IndexError:
            return False
        endpoint = f"/api/v1/cards/{self.data.id}/checklist/{checklist['id']}/"
        return ppcurses.delete(endpoint)

    def edit_checklist(self, index):
        if self.data.id is None:
            return False
        try:
            checklist = self.data.checklist[index]
        except IndexError:
            return False
        logger.warning('pending: editing checklist')

    def add_checklist(self):
        if self.data.id is None:
            return False
        logger.warning('pending: adding checklist')

    def checklist_to_card(self, index):
        if self.data.id is None:
            return False
        try:
            checklist = self.data.checklist[index]
        except IndexError:
            return False
        logger.warning('pending: convert checklist to card')

    def move_to_column(self, index):
        if self.data.id is None:
            return False

    def move_to_planlet(self, index):
        if self.data.id is None:
            return False

    def change_title(self):
        if self.data.id is None:
            return False
        logger.warning('pending: changing title')

    def change_description(self):
        if self.data.id is None:
            return False
        logger.warning('pending: changing description')

    def change_points(self):
        if self.data.id is None:
            return False
        points = ['remove', 0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 100]
        data = [{'id': x, 'name': str(x)} for x in points]
        response = ppcurses.hover.select_one('point', lambda **kwargs: data)
        if response is not None:
            endpoint = f"/api/v1/cards/{self.data.id}"
            data = {'estimate': response['id']}
            return ppcurses.put(endpoint, data)

    def change_label(self):
        if self.data.id is None:
            return False
        response = ppcurses.hover.select_one('label', lambda **kwargs:  ppcurses.memstore['board'].labels)
        if response is not None:
            endpoint = f"/api/v1/cards/{self.data.id}"
            data = {'label_id': response['id']}
            return ppcurses.put(endpoint, data)

    def change_assignee(self):
        if self.data.id is None:
            return False
        board_id = ppcurses.memstore['board'].id
        project_id = ppcurses.dbstore['project_id']
        endpoint = f"/api/v2/boards/{board_id}/people-with-access"
        allowed = ppcurses.get(endpoint, refetch=True)['access']

        endpoint = f"/api/v1/projects/{project_id}/members?member_params=include_last_active,include_pending,organisation,description,in_team"
        allowed_members = [{'id': member['id'],
                            'name': member['name']
                            } for member in ppcurses.get(endpoint, refetch=True) if member['id'] in allowed]
        response = ppcurses.hover.select_one('assignee', lambda **kwargs: allowed_members)
        if response is not None:
            endpoint = f"/api/v1/cards/{self.data.id}"
            data = {'assignee_id': response['id']}
            return ppcurses.put(endpoint, data)

    def change_co_assignee(self):
        if self.data.id is None:
            return False
        logger.warning('pending: changing co-assignee')


class Comments(Pager):
    zerostate = [Zero('No comments to show')]

    def generate_lines_of_text(self):
        contents = []
        for n, comment in enumerate(self.data):
            if comment.id is None:
                contents.append(comment.text)
                continue
            contents.append(str(n) + '. ' + ppcurses.epoch_to_datetime(comment.created_at))
            contents.append('By: %s' % comment.created_by['name'])
            if comment.attachments:
                contents.append('Attachments: %s' % comment.attachments)

            for line in comment.text.split('\n'):
                contents.extend(textwrap.wrap(line, width=self.window.maxx-5))
            if n != (len(self.data) - 1):
                contents.append(' ')
                contents.append('-'*(self.window.maxx-5))
                contents.append(' ')

        return contents

    def delete(self, index):
        try:
            comment = self.data[index]
        except IndexError:
            return False
        if comment.id is None:
            return False

        if not comment.is_mine():
            logger.warning('Trying to modify a card that you did not create')
            return False

        card_id = ppcurses.memstore['card'].id
        endpoint = f"/api/v3/conversations/comment/{comment.id}?item_id={card_id}&item_name=card"
        return ppcurses.delete(endpoint)

    def edit(self, index):
        try:
            comment = self.data[index]
        except IndexError:
            return False
        if comment.id is None:
            return False
        logger.warning('pending: editing comment %s', index)

    def add(self):
        if ppcurses.memstore['card'].data.id is None:
            return
        logger.warning('pending: adding a comment')
