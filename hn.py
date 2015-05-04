#!/usr/bin/env python
import os
import json
import urllib2

import arrow
import rethinkdb


MAIN_ID = '9471287' # '9303396' # '9127232' #'8980047'
TEMPLATE = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
DB_HOST = 'localhost'
DB_PORT = 28015
DB_DATABASE = 'hnjobs'

def get_all(start_id=None, seen=None):
    ids = [start_id or MAIN_ID]
    seen = set(seen or []).difference(ids)

    failed = []

    while ids:
        hn_id = ids.pop()
        if hn_id in seen:
            continue

        seen.add(hn_id)
        try:
            x = urllib2.urlopen(TEMPLATE.format(hn_id))
            data = json.loads(x.read())
            x.close()
        except Exception as error:
            print hn_id, type(error), error
            failed.append(hn_id)
            continue

        if 'text' in data:
            data['id'] = str(data['id'])
            yield data

        if 'kids' in data:
            ids += data['kids']

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
