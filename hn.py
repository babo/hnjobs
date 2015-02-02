#!/usr/bin/env python
import arrow
from elasticsearch import Elasticsearch
import os
import json
import urllib2

MAIN_ID = '8980047'
TEMPLATE = 'https://hacker-news.firebaseio.com/v0/item/{}.json'

def main():
    es = Elasticsearch()
    es.indices.create(index='hn-index', ignore=400)

    failed = []
    seen = set()
    ids = [MAIN_ID]

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
            print hn_id, data['text'].encode('utf-8')

            data['timestamp'] = arrow.get(data['time'])
            r = es.index(index='hn-index', doc_type='job-type', id=data['id'], body=data}

        if 'kids' in data:
            ids += data['kids']


if __name__ == '__main__':
    main()
