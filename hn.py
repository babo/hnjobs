#!/usr/bin/env python
import arrow
from elasticsearch import Elasticsearch

import pyArango.connection

import os
import json
import urllib2

MAIN_ID = '8980047'
TEMPLATE = 'https://hacker-news.firebaseio.com/v0/item/{}.json'

def get_all(start_id=None, seen=None):
    seen = set(seen or [])
    failed = []

    ids = [start_id or MAIN_ID]

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
            print data
            yield data

        if 'kids' in data:
            ids += data['kids']

def get_collection():
    conn = pyArango.connection.Connection()
    if 'hn_db' not in conn.databases:
        conn.createDatabase(name='hn_db')
    db = conn.databases['hn_db']

    if 'jobs' not in db.collections:
        db.createCollection(name = 'jobs')
    collection = db.collections['jobs']
    return collection

def main():
    collection = get_collection()

    seen = [q._key for q in collection.fetchAll()]
    for data in get_all(seen=seen):
        jid = str(data['id'])
        try:
            collection.fetchDocument(jid)
            continue
        except KeyError:
            pass

        doc = collection.createDocument({'_key': jid})
        for k, v in data.items():
            doc[k] = v
        doc.save()
        print jid

if __name__ == '__main__':
    main()
