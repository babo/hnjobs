#!/usr/bin/env python
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

import latest_post

MAIN_ID = latest_post.who_is_hiring_thread()
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

    navmode = request.args.get('navmode', '0')
    if navmode == '2':
        filter_f = lambda x: x['cool'] == 0
    elif navmode == '1':
        filter_f = lambda x: x['cool'] > 1
    else:
        filter_f = lambda x: x['cool'] == 1

    jobfilter = request.args.get('filter', "")
    filter_q = lambda x: x['text'].match("(?im)"+jobfilter)

    cursor = table.filter({'parent': int(MAIN_ID), 'type': 'comment'}).filter(filter_f).filter(filter_q).with_fields('text', 'by', 'time', 'cool', 'id').limit(LIMIT).run(c)
    jobs = list(cursor)

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

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT",3000)), debug=True)
