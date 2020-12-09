#!/usr/bin/env python
from ppcurses.utils import get


def projects():
    endpoint = '/1/user/me/projects'
    data = [{'id': each['id'], 'name': each['name']} for each in get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def boards(project_id):
    endpoint = '/1/user/me/boards/ongoing'
    data = [{'id': each['id'], 'name': each['name']} for each in get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def planlets(board_id):
    endpoint = '/1/boards/%s/planlets' % board_id
    data = [{'id': each['id'], 'name': each['name']} for each in get(endpoint)[str(board_id)]]
    data.sort(key=lambda x: x['name'])
    return data


def cards(board_id, planlet_id):
    endpoint = '/1/boards/%s/cards' % board_id
    data = [{'id': each['id'], 'name': each['title']} for each in get(endpoint) if each['planlet_id'] in (None, planlet_id)]
    data.sort(key=lambda x: x['name'])
    return data


if __name__ == '__main__':
    import doctest
    doctest.testmod()
