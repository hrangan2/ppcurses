#!/usr/bin/env python
import configparser

parser = configparser.ConfigParser()
parser.read_file(open('/Users/hrangan/.secrets/keys'))
token = parser.get('ppcli', 'token')
domain = parser.get('ppcli', 'domain')
