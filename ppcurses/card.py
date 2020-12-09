#!/usr/bin/env python
from ppcurses.utils import get
import json


class Base:
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


class Card(Base):
    def __init__(self, card_id):
        self.load_card(card_id)
        self.load_comments(card_id)

    def load_card(self, card_id):
        card = get(f'/1/cards/{card_id}')
        tags = get(f'/1/tags/cards/{card_id}')

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
        comments = get(f'/3/conversations/comments?item_id={card_id}&item_name=card&count=100&offset=0')
        self.comments = [Comment(each) for each in comments['data']]


class Comment(Base):
    def __init__(self, comment):
        self.id = comment['id']
        self.text = comment['text']
        self.created_at = comment['created_at']
        self.created_by = {
                'id': comment['created_by']['id'],
                'name': ' '.join([comment['created_by']['first_name'], comment['created_by']['last_name']])
                }
        self.attachments = len(comment.get('attachments', []))


if __name__ == '__main__':
    print(Card(30123))
