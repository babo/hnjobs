#!/usr/bin/env python
import os
import json
import urllib2

import arrow

from elasticsearch import Elasticsearch
from arango import Arango


MAIN_ID = '8980047'
TEMPLATE = 'https://hacker-news.firebaseio.com/v0/item/{}.json'

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
            yield data

        if 'kids' in data:
            ids += data['kids']

def get_collection():
    connection = Arango()
    if 'hn_db' not in connection.databases['user']:
        connection.add_database('hn_db')
    db = connection.database('hn_db')

    if 'jobs' not in db.collections['user']:
        db.add_collection('jobs')
    return db.collection('jobs')

def main():
    collection = get_collection()

    seen = [x['_key'] for x in collection.all()]
    for data in get_all(seen=seen):
        jid = str(data['id'])
        if not collection.contains(jid):
            data['_key'] = jid
            collection.add_document(data)
            print 'new', jid
        else:
            print 'seen', jid

if __name__ == '__main__':
    main()
