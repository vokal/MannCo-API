#!/usr/bin/env python3

import atexit
import json
import os
from urllib.parse import urlparse

import pymysql
import pymysql.cursors

DATABASE_URL = os.getenv('DATABASE_URL')

## arg handling
parsed = urlparse(DATABASE_URL)

host = parsed.hostname
port = parsed.port
username = parsed.username
password = parsed.password
port = parsed.port
db =  parsed.path[1:] # ignore / on /tf2stats


## Connect to the database
connection = pymysql.connect(host=host,
                             user=username,
                             password=password,
                             db=db,
                             charset='utf8',
                             cursorclass=pymysql.cursors.DictCursor)
## close connection on exit
atexit.register(lambda: connection.close())


## so I don't have to care about cursors
def sql(*args):
    connection.ping(True)
    with connection.cursor() as cursor:
        cursor.execute(*args)
        return cursor.fetchall()

def sql_value(*args):
    return sql(*args)[0].get('value')
