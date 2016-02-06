#!/usr/bin/env python3
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# FACEBOOK BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Retrieving jobs from the monthly "Ask HN: Who is hiring?" on Hacker News
"""
import json
import time

from contextlib import closing
from urllib.request import urlopen

import rethinkdb


IDS = ['11012044', '10822019', '10655740', '10492086', '10311580', '10152809', '9996333', '9639001', '9471287', '9303396', '9127232', '8980047']
MAIN_ID = IDS[0]
TEMPLATE = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
WHO_IS_HIRING = 'https://hacker-news.firebaseio.com/v0/user/whoishiring.json'

DB_HOST = 'localhost'
DB_PORT = 28015
DB_DATABASE = 'hnjobs'
MAX_RETRIES = 5

class FireBaseException(Exception):
    pass

def read_firebase(hn_url):
    try:
        for i in range(MAX_RETRIES + 1):
            with closing(urlopen(hn_url)) as x:
                if x.getcode() / 100 == 5 and i < MAX_RETRIES:
                    time.sleep(0.2 * 2 ** i)
                elif x.getcode() / 100 == 2:
                    return json.loads(x.read().decode('utf-8'))
                else:
                    raise FireBaseException(x.code)
    except Exception as error:
        print(hn_id, type(error), error)

def latest_thread():
    submitted = map(int, read_firebase(WHO_IS_HIRING)['submitted'])

    # check submissions in cronological order
    for hn_id in sorted(submitted, reverse=True):
        post_data = read_firebase(TEMPLATE.format(hn_id))
        if 'title' in post_data and 'Ask HN: Who is hiring?' in post_data['title']:
            print(post_data['title'])
            return hn_id

def get_all(start_id=None, seen=None):
    ids = [start_id or MAIN_ID]
    seen = set(seen or []).difference(ids)

    failed = []

    while ids:
        hn_id = ids.pop()
        if hn_id in seen:
            continue

        data = read_firebase(TEMPLATE.format(hn_id))
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
        print('Failed', failed)

def init_db():
    c = rethinkdb.connect(host=DB_HOST, port=DB_PORT)
    if DB_DATABASE not in rethinkdb.db_list().run(c):
        x = rethinkdb.db_create(DB_DATABASE).run(c)
        if x.get('dbs_created', 0) != 1:
            raise Exception('Unable to create database')
    c = rethinkdb.connect(host=DB_HOST, port=DB_PORT, db=DB_DATABASE)

    if DB_THREAD_IDS not in rethinkdb.table_list().run(c):
        x = rethinkdb.table_create(DB_THREAD_IDS).run(c)
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
                print('Fail to add {} {}'.format(jid, x))
            else:
                print('new {}'.format(jid))
        else:
            print('seen {}'.format(jid))

if __name__ == '__main__':
    main()
