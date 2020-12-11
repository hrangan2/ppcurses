#!/usr/bin/env python
import logging
import ppcurses.model
from ppcurses import domain
from ppcurses.utils import get
from ppcurses.errors import CallFailure


logger = logging.getLogger(__name__)


def quickfail_dns():
    """Fail quickly when encountering a DNS issue"""
    import socket
    import signal

    def callback():
        raise CallFailure('DNS_TIMEOUT')

    signal.signal(signal.SIGALRM, callback)
    signal.alarm(1)
    socket.gethostbyname(domain)
    signal.alarm(0)


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
    logger.info('Calling endpoint %s', endpoint)
    data = [{'id': each['id'], 'name': each['name']} for each in get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def boards(project_id):
    endpoint = f"/1/projects/{project_id}/boards"
    logger.info('Calling endpoint %s', endpoint)
    data = [{
        'id': each['id'],
        'name': each['name'],
        'project_id': project_id,
        'board_id': each['id']
        } for each in get(endpoint)]
    data.sort(key=lambda x: x['name'])
    return data


def planlets(kwargs):
    endpoint = f"/1/boards/{kwargs['board_id']}/planlets"
    logger.info('Calling endpoint %s', endpoint)
    data = [{
        'id': each['id'],
        'name': each['name'],
        'project_id': kwargs['project_id'],
        'board_id': kwargs['board_id'],
        'planlet_id': each['id']
        } for each in get(endpoint)[str(kwargs['board_id'])]]
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
    internal_endpoint = f"/1/boards/{kwargs['board_id']}/properties"
    logger.info('Calling endpoint %s', internal_endpoint)
    return [{
        'id': each['id'],
        'name': each['name'],
        'project_id': kwargs['project_id'],
        'board_id': kwargs['board_id'],
        'planlet_id': kwargs['planlet_id'],
        'column_id': each['id']
        } for each in ppcurses.model.Board(kwargs['board_id']).progresses]


def cards(kwargs):
    endpoint = f"/1/boards/{kwargs['board_id']}/cards"
    logger.info('Calling endpoint %s', endpoint)
    logger.error(kwargs['planlet_id'])
    data = [{
        'id': each['id'],
        'name': each['title'],
        'project_id': kwargs['project_id'],
        'board_id': kwargs['board_id'],
        'planlet_id': kwargs['planlet_id'],
        'column_id': kwargs['column_id'],
        'card_id': each['id']
        } for each in get(endpoint)
        if ((each['planlet_id'] or -1) == kwargs['planlet_id'])
        and each['column_id'] == kwargs['column_id']]
    data.sort(key=lambda x: x['name'])
    return data


if __name__ == '__main__':
    import doctest
    doctest.testmod()
