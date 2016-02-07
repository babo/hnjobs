#!/usr/bin/env python3
# This file provided by Facebook is for non-commercial testing and evaluation purposes only.
# Facebook reserves all rights not expressly granted.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# FACEBOOK BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import json
import os

import rethinkdb

from flask import Flask, Response, request

from hn import MAIN_ID

LIMIT = 700
DB_HOST = 'localhost'
DB_PORT = 28015
DB_DATABASE = 'hnjobs'

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('./index.html'))

@app.route('/hnjobs', methods=['GET'])
def comments_handler():
    c = rethinkdb.connect(host=DB_HOST, port=DB_PORT, db=DB_DATABASE)
    table = rethinkdb.table(MAIN_ID)

    cursor = table.filter({'parent': int(MAIN_ID), 'type': 'comment'})

    navmode = request.args.get('navmode', '0')
    if navmode == '2':
        cursor = cursor.filter({'cool': 0})
    elif navmode == '1':
        cursor = cursor.filter(rethinkdb.row['cool'].gt(1))
    elif navmode == '3':
        cursor = cursor.filter({'cool': 1}).filter(rethinkdb.row['text'].match('(?i)remote'))
    else:
        cursor = cursor.filter({'cool': 1})

    jobfilter = request.args.get('filter', None)
    if jobfilter:
        cursor = cursor.filter(rethinkdb.row['text'].match(r'(?i){}'.format(jobfilter)))

    jobs = list(cursor.limit(LIMIT).run(c))

    return Response(json.dumps(jobs), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

@app.route('/hnjobs/latest', methods=['GET'])
def latest_handler():
    c = rethinkdb.connect(host=DB_HOST, port=DB_PORT, db=DB_DATABASE)
    table = rethinkdb.table(MAIN_ID)

    counters = table.group('cool').count().run(c)
    rtv = {'url': 'https://news.ycombinator.com/item?id={}'.format(MAIN_ID),
        'total': table.count().run(c),
        'date': table.get(MAIN_ID).run(c)['time'],
        'latest': table.filter({'parent': int(MAIN_ID)}).max('time').run(c)['time'],
        'liked': counters[2],
        'disliked': counters[0],
        'unclassified': counters[1],
        'total': sum(counters.values())
    }

    return Response(json.dumps(rtv), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

@app.route('/hnjobs/update/<jobid>', methods=['DELETE', 'POST'])
def hide_a_job_handler(jobid):
    c = rethinkdb.connect(host=DB_HOST, port=DB_PORT, db=DB_DATABASE)
    table = rethinkdb.table(MAIN_ID)

    success = False
    if request.method == 'DELETE':
        rtv = table.get(jobid).update({'cool': 0}).run(c)
        success = rtv.get('skipped', 1) == 0
        app.logger.debug('Hide {} {}'.format(jobid, rtv))
    elif request.method == 'POST':
        rtv = table.get(jobid).update({'cool': rethinkdb.row['cool'] + 1}).run(c)
        success = rtv.get('skipped', 1) == 0
        app.logger.debug('Updated {} {}'.format(jobid, rtv))
    rtv = {'success': success}
    return Response(json.dumps(rtv), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

def main():
    app.run(port=int(os.environ.get('PORT', 3000)), debug=True)

if __name__ == '__main__':
    main()
