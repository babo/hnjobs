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

import hn

LIMIT = 700

app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('./index.html'))

@app.route('/hnjobs', methods=['GET'])
def comments_handler():
    cursor = app.table.filter({'parent': app.main_id, 'type': 'comment'})

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

    jobs = list(cursor.limit(LIMIT).run(app.connection))

    return Response(json.dumps(jobs), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

@app.route('/hnjobs/latest', methods=['GET'])
def latest_handler():
    counters = app.table.group('cool').count().run(app.connection)
    rtv = { \
        'url': 'https://news.ycombinator.com/item?id={}'.format(app.main_id),
        'date': app.table.get(app.main_id).run(app.connection)['time'],
        'latest': app.table.filter({'parent': app.main_id}).max('time').run(app.connection)['time'],
        'liked': counters[2],
        'disliked': counters[0],
        'unclassified': counters[1],
        'total': sum(counters.values())}

    return Response(json.dumps(rtv), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

@app.route('/hnjobs/update/<jobid>', methods=['DELETE', 'POST'])
def hide_a_job_handler(jobid):

    success = False
    try:
        jobid = int(jobid)
        if request.method == 'DELETE':
            rtv = app.table.get(jobid).update({'cool': 0}).run(app.connection)
            success = rtv.get('skipped', 1) == 0
            app.logger.debug('Hide {} {}'.format(jobid, rtv))
        elif request.method == 'POST':
            rtv = app.table.get(jobid).update({'cool': rethinkdb.row['cool'] + 1}).run(app.connection)
            success = rtv.get('skipped', 1) == 0
            app.logger.debug('Updated {} {}'.format(jobid, rtv))
        rtv = {'success': success}
    except ValueError:
        pass
    return Response(json.dumps(rtv), mimetype='application/json', headers={'Cache-Control': 'no-cache'})

def main():
    app.connection, app.table, app.main_id = hn.get_connection()
    app.run(port=int(os.environ.get('PORT', 3000)), debug=True)

if __name__ == '__main__':
    main()
