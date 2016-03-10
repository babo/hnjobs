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
import argparse
import datetime
import json
import time

from contextlib import closing
from urllib.request import urlopen

import rethinkdb
from pytz import timezone

TEMPLATE = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
WHO_IS_HIRING = 'https://hacker-news.firebaseio.com/v0/user/whoishiring.json'

DB_HOST = 'localhost'
DB_PORT = 28015
DB_DATABASE = 'hnjobs'
DB_THREAD_IDS = 'threads'
MAX_RETRIES = 5

class FireBaseException(Exception):
    "FireBase connection error"
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
        print(hn_url, type(error), error)
        raise

def get_all(main_id, seen):
    ids = [main_id]
    failed = []

    while ids:
        hn_id = ids.pop()
        if hn_id != main_id and hn_id in seen:
            continue

        data = read_firebase(TEMPLATE.format(hn_id))
        seen.add(hn_id)

        if data is None:
            failed.append(hn_id)
        else:
            if 'text' in data:
                yield data

            if 'kids' in data:
                ids += data['kids']

    if failed:
        print('Failed', failed)

def get_date(year=None, month=None):
    # It's published on the first day of the month at 9am EST
    est = timezone('US/Eastern')
    now = datetime.datetime.now(tz=est)
    if year or month:
        if year is None:
            year = now.year
        if month is None:
            month = now.month
        when = datetime.datetime(year or now.year, month or now.month, 1, 9, 0, 0, 0, est)
    elif now.day == 1 and now.hour < 9:
        print("It's not published yet, check back in {} hours".format(9 - now.hour))
        when = now - datetime.timedelta(1)
    else:
        when = now
    return when

def date2key(when):
    return when.strftime('%Y-%m')

def validate_thread_id(connection, hn_id):
    cursor = rethinkdb.table(DB_THREAD_IDS).filter({'thread_id': hn_id}).run(connection)
    if cursor.items:
        key = cursor.next()['id']
        cursor.close()
        when = get_date(*[int(x) for x in key.split('-')])
    else:
        post_data = read_firebase(TEMPLATE.format(hn_id))
        when = datetime.datetime.fromtimestamp(post_data['time'])
        thread_id = {'id': date2key(when), 'thread_id': hn_id}
        rethinkdb.table(DB_THREAD_IDS).insert(thread_id).run(connection)
    return hn_id

def get_latest_thread(connection, year=None, month=None):
    when = get_date(year, month)
    key = date2key(when)
    thread_id = rethinkdb.table(DB_THREAD_IDS).get(key).run(connection)
    if thread_id is None:
        monthly_title = when.strftime('Ask HN: Who is hiring? (%B %Y)')
        submitted = [int(x) for x in read_firebase(WHO_IS_HIRING)['submitted']]

        # check submissions in cronological order
        for hn_id in sorted(submitted, reverse=True):
            post_data = read_firebase(TEMPLATE.format(hn_id))
            print(post_data['title'] if 'title' in post_data else post_data)
            if 'title' in post_data and monthly_title in post_data['title']:
                thread_id = {'id': key, 'thread_id': hn_id}
                rethinkdb.table(DB_THREAD_IDS).insert(thread_id).run(connection)
                break
        else:
            raise Exception('There is no "{}" found'.format(monthly_title))

    return thread_id['thread_id']

def get_main_id(connection, args):
    args = check_args()

    if args.thread_id:
        thread_id = validate_thread_id(connection, args.thread_id)
    else:
        thread_id = get_latest_thread(connection, args.year, args.month)
    if str(thread_id) not in rethinkdb.table_list().run(connection):
        x = rethinkdb.table_create(str(thread_id)).run(connection)
        if x.get('tables_created', 0) != 1:
            raise Exception('Unable to create table {}'.format(thread_id))
    return thread_id

def init_db():
    connection = rethinkdb.connect(host=DB_HOST, port=DB_PORT)
    if DB_DATABASE not in rethinkdb.db_list().run(connection):
        x = rethinkdb.db_create(DB_DATABASE).run(connection)
        if x.get('dbs_created', 0) != 1:
            raise Exception('Unable to create database')
    c = rethinkdb.connect(host=DB_HOST, port=DB_PORT, db=DB_DATABASE)

    if DB_THREAD_IDS not in rethinkdb.table_list().run(connection):
        x = rethinkdb.table_create(DB_THREAD_IDS).run(connection)
        if x.get('tables_created', 0) != 1:
            raise Exception('Unable to create table {}'.format(DB_THREAD_IDS))

    return c

def check_args():
    parser = argparse.ArgumentParser(description='Read monthly who is hiring thread from hacker new')
    parser.add_argument('-y', '--year', type=int, dest='year', action='store', default=None, help='from 2012, default is the current')
    parser.add_argument('-m', '--month', type=int, dest='month', action='store', default=None, help='as an integer, default is the current')
    parser.add_argument('-t', '--thread', type=int, dest='thread_id', action='store', default=None, help='thread id as an integer, default is the current')

    return parser.parse_args()

def get_connection():
    args = check_args()
    connection = init_db()
    main_id = get_main_id(connection, args)
    table = rethinkdb.table(str(main_id))
    return connection, table, main_id

def main():
    connection, table, main_id = get_connection()

    cur = table.with_fields('id').run(connection)
    seen = set([x['id'] for x in cur])
    for data in get_all(main_id, seen):
        jid = data['id']
        if jid not in seen:
            data['cool'] = 1
            x = table.insert(data).run(connection)
            if x.get('inserted', 0) != 1:
                print('Fail to add {} {}'.format(jid, x))
            else:
                print('new {}'.format(jid))
        elif jid != main_id:
            print('seen {}'.format(jid))

if __name__ == '__main__':
    main()
