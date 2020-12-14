#!/usr/bin/env python
import json
import signal
import logging
import ppcurses
from ppcurses.errors import CallFailure


logger = logging.getLogger(__name__)


def network_quickfail():
    def handler(signum, frame):
        raise CallFailure('NETWORK QUICKFAIL')
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(2)
    me()
    signal.alarm(0)


def fileinit():
    return [{
            "id": '%s: %s' % (ppcurses.dbstore['project_id'], ppcurses.dbstore['board_id']),
            "project_id": ppcurses.dbstore['project_id'],
            "project_name": ppcurses.dbstore['project_name'],
            "board_id": ppcurses.dbstore['board_id'],
            "board_name": ppcurses.dbstore['board_name']
            }]


def me():
    endpoint = '/1/user/me/profile'
    data = ppcurses.get(endpoint)
    return {'id': data['id'],
            'name': data['sort_name'],
            'user_id': data['id']
            }


def projects():
    endpoint = '/1/user/me/projects'
    data = [{'id': each['id'],
             'name': each['name'],
             'project_id': each['id']} for each in ppcurses.get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def boards(kwargs):
    endpoint = f"/1/projects/{kwargs['project_id']}/boards"
    data = [{
        'id': each['id'],
        'name': each['name'],
        'project_id': kwargs['project_id'],
        'board_id': each['id']
        } for each in ppcurses.get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def planlets(kwargs):
    endpoint = f"/1/boards/{kwargs['board_id']}/planlets"
    data = [{
        'id': each['id'],
        'name': each['name'],
        'project_id': kwargs['project_id'],
        'board_id': kwargs['board_id'],
        'planlet_id': each['id']
        } for each in ppcurses.get(endpoint)[str(kwargs['board_id'])]]
    data.sort(key=lambda x: x['name'])
    data.append({
        'id': -1,
        'name': 'No Activity',
        'project_id': kwargs['project_id'],
        'board_id': kwargs['board_id'],
        'planlet_id': -1
        })
    return data


def columns(kwargs):
    columns = Board(kwargs['board_id']).progresses
    ppcurses.memstore['columns'] = columns
    return [{
        'id': each['id'],
        'name': each['name'],
        'project_id': kwargs['project_id'],
        'board_id': kwargs['board_id'],
        'planlet_id': kwargs['planlet_id'],
        'column_id': each['id']
        } for each in columns]


def cards(kwargs):
    endpoint = f"/1/boards/{kwargs['board_id']}/cards"
    data = [{
        'id': each['id'],
        'name': each['title'],
        'project_id': kwargs['project_id'],
        'board_id': kwargs['board_id'],
        'planlet_id': kwargs['planlet_id'],
        'column_id': kwargs['column_id'],
        'card_id': each['id']
        } for each in ppcurses.get(endpoint)
        if ((each['planlet_id'] or -1) == kwargs['planlet_id'])
        and each['column_id'] == kwargs['column_id']]
    data.sort(key=lambda x: x['name'])
    return data


def comments(kwargs):
    endpoint = f"/3/conversations/comments?item_id={kwargs['card_id']}&item_name=card&count=100&offset=0"
    return [Comment(each) for each in ppcurses.get(endpoint)['data']]


class Serializer:
    def __setattr__(self, key, value):
        if not hasattr(self, '_fields'):
            super().__setattr__('_fields', set())
        super().__setattr__(key, value)
        self._fields.add(key)

    def serialize(self):
        if not hasattr(self, '_fields'):
            return {}
        return {field: getattr(self, field) for field in self._fields}

    def __repr__(self):
        return str(self.serialize())

    def __str__(self):
        return json.dumps(self.serialize(), indent=4, default=lambda x: x.serialize())


class Card(Serializer):
    def __init__(self, kwargs):
        card_id = kwargs['card_id']
        self.load_card(card_id)
        self.load_comments(card_id)

    def load_card(self, card_id):
        card = ppcurses.get(f'/1/cards/{card_id}')
        tags = ppcurses.get(f'/1/tags/cards/{card_id}')

        self.id = card['id']
        self.title = card['title']

        self.description = card['description']

        if card.get('assignee', None) is not None:
            self.assignee = {
                    "id": card['assignee']['id'],
                    "name": card['assignee']['name']
                    }
        else:
            self.assignee = None

        self.contributors = [{'id': each['id'], 'name': each['name']} for each in card.get('contributors', [])]

        if card.get('label_id', None) is not None:
            self.label = {
                    'id': card['label_id'],
                    'name': card['label_name']
                    }
        else:
            self.label = None

        self.estimate = card.get('estimate', None)

        if card.get('checklist', None) is not None:
            self.checklist = []
            for each in card['checklist']['items']:
                self.checklist.append({
                    'id': each['id'],
                    'done': each['done'],
                    'title': each['title'],
                    'order': each['order']
                    })
            self.checklist.sort(key=lambda x: x['order'])
        else:
            self.checklist = None

        self.tags = tags

    def load_comments(self, card_id):
        comments = ppcurses.get(f'/3/conversations/comments?item_id={card_id}&item_name=card&count=100&offset=0')
        self.comments = [Comment(each) for each in comments['data']]


class Comment(Serializer):
    def __init__(self, comment):
        self.id = comment['id']
        self.text = comment['text']
        self.created_at = comment['created_at']
        self.created_by = {
                'id': comment['created_by']['id'],
                'name': ' '.join([comment['created_by']['first_name'], comment['created_by']['last_name']])
                }
        self.attachments = len(comment.get('attachments', []))


class Board(Serializer):
    def __init__(self, board_id):
        self.load_board(board_id)

    def load_board(self, board_id):
        board = ppcurses.get(f'/1/boards/{board_id}/properties')

        self.id = board['id']
        self.name = board['name']
        self.labels = board['labels']
        self.progresses = []
        for each in sorted(board['progresses'], key=lambda x: x['display_order']):
            self.progresses.append({
                'id': each['id'],
                'name': each['name']
                })

        self.labels = []
        for each in sorted(board['labels'], key=lambda x: x['display_order']):
            self.labels.append({
                'id': each['id'],
                'name': each['name']
                })
