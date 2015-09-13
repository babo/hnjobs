#!/usr/bin/env python
import os
import json
import time
import urllib2

from contextlib import closing

import arrow
import rethinkdb


MAIN_ID = '10152809' # '9996333' # '9639001' # 9471287' # '9303396' # '9127232' #'8980047'
TEMPLATE = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
DB_HOST = 'localhost'
DB_PORT = 28015
DB_DATABASE = 'hnjobs'
MAX_RETRIES = 5

class FireBaseException(Exception):
    pass

def read_comment(hn_id):
    try:
        for i in range(MAX_RETRIES + 1):
            with closing(urllib2.urlopen(TEMPLATE.format(hn_id))) as x:
                if x.getcode() / 100 == 5 and i < MAX_RETRIES:
                    time.sleep(0.2 * 2 ** i)
                elif x.getcode() / 100 == 2:
                    return json.loads(x.read())
                else:
                    raise FireBaseException(x.code)
    except Exception as error:
        print hn_id, type(error), error

def get_all(start_id=None, seen=None):
    ids = [start_id or MAIN_ID]
    seen = set(seen or []).difference(ids)

    failed = []

    while ids:
        hn_id = ids.pop()
        if hn_id in seen:
            continue

        data = read_comment(hn_id)
        seen.add(hn_id)

        if data is None:
            failed.append(hn_id)
        else:
            if 'text' in data:
                data['id'] = str(data['id'])
                yield data

            if 'kids' in data:
                ids += data['kids']

    if failed:
        print 'Failed', failed

def init_db():
    c = rethinkdb.connect(host=DB_HOST, port=DB_PORT, db=DB_DATABASE)

    if 'hnjobs' not in rethinkdb.db_list().run(c):
        x = rethinkdb.db_create('hnjobs').run(c)
        if x.get('dbs_created', 0) != 1:
            raise Exception('Unable to create database')

    if MAIN_ID not in rethinkdb.db('hnjobs').table_list().run(c):
        x = rethinkdb.db('hnjobs').table_create(MAIN_ID).run(c)
        if x.get('tables_created', 0) != 1:
            raise Exception('Unable to create table {}'.format(MAIN_ID))

    return c

def main():
    c = init_db()
    table = rethinkdb.table(MAIN_ID)

    cur = table.with_fields('id').run(c)
    seen = set([x['id'] for x in cur])
    for data in get_all(seen=seen):
        jid = data['id']
        if jid not in seen:
            data['cool'] = 1
            x = table.insert(data).run(c)
            if x.get('inserted', 0) != 1:
                print 'Fail to add {} {}'.format(jid, x)
            else:
                print 'new {}'.format(jid)
        else:
            print 'seen {}'.format(jid)

if __name__ == '__main__':
    main()
