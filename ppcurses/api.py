#!/usr/bin/env python
from ppcurses.utils import get
from ppcurses.model import Board, Card


def staticinit():
    return [{
            "id": "148:1",
            "project_id": 148,
            "project_name": 'meetings',
            "board_id": 1,
            "board_name": 'board 1'
            }]


def projects():
    endpoint = '/1/user/me/projects'
    data = [{'id': each['id'], 'name': each['name']} for each in get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def boards(project_id):
    endpoint = f'/1/projects/{project_id}/boards'
    data = [{'id': each['id'], 'name': each['name']} for each in get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def planlets(board_id):
    endpoint = f'/1/boards/{board_id}/planlets'
    data = [{'id': each['id'], 'name': each['name']} for each in get(endpoint)[str(board_id)]]
    data.sort(key=lambda x: x['name'])
    return data


def columns(board_id):
    return Board(board_id).progresses


def cards(board_id, planlet_id, column_id):
    endpoint = '/1/boards/%s/cards' % board_id
    data = [{'id': each['id'], 'name': each['title']} for each in get(endpoint) if each['planlet_id'] in (None, planlet_id)]
    data.sort(key=lambda x: x['name'])
    return data


def card(card_id):
    return Card(card_id)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
