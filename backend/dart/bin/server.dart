import 'package:redstone/server.dart' as app;
import 'package:rethinkdb_driver/rethinkdb_driver.dart';
//import 'package:redstone_rethinkdb/redstone_rethinkdb.dart';
import 'package:shelf_static/shelf_static.dart';
import 'dart:async';

final Rethinkdb r = new Rethinkdb();
final String MAIN_ID = '9471287';
final LIMIT = 7;
final DB_HOST = 'localhost';
final DB_PORT = 28015;
final DB_DATABASE = 'hnjobs';

@app.Route('/hnjobs')
commentsHandler(@app.QueryParam('navmode') int navmode) {
    var filter_f;

    switch(navmode) {
        case 2:
            filter_f = (x) => x('cool').eq(0);
            break;
        case 1:
            filter_f = (x) => x('cool').gt(1);
            break;
        default:
            filter_f = (x) => x('cool').eq(1);
            break;
    }

    return r.connect(db: DB_DATABASE, port: DB_PORT, host: DB_HOST)
        .then((connection) async {
            var rtv = await r.table(MAIN_ID)
                .filter(r.row('parent').eq(int.parse(MAIN_ID)))
                .filter(r.row('type').eq('comment'))
                .filter(filter_f)
                .limit(LIMIT)
                .withFields(['text', 'by', 'time', 'cool', 'id'])
                .run(connection)
                .then((cursor) => cursor.toArray());
            connection.close();
            return rtv;
        })
        .catchError((err) {
            print(err);
            return [];
        });
}

@app.Route('/hnjobs/update/:jobid', methods: const [app.POST, app.DELETE])
like_a_job(String jobid) =>
    r.connect(db: DB_DATABASE, port: DB_PORT, host: DB_HOST)
        .then((connection) async {
            var rtv = await r.table(MAIN_ID)
                .get(jobid)
                .update({'cool': app.request.method == app.POST ? r.row('cool').add(1) : 0})
                .run(connection);
            connection.close();
            return {'success': rtv('skipped') == 0};
        });

@app.Route('/hnjobs/latest', methods: const [app.GET])
latest() =>
    r.connect(db: DB_DATABASE, port: DB_PORT, host: DB_HOST)
        .then((connection) async {
            var f1 = r.table(MAIN_ID)
                .filter(r.row('parent').eq(int.parse(MAIN_ID)))
                .max('time')
                .run(connection);

            var f2 = r.table(MAIN_ID)
                    .filter(r.row('parent').eq(int.parse(MAIN_ID)))
                    .min('time')
                    .run(connection);

            var f3 =  r.table(MAIN_ID)
                    .group('cool')
                    .count()
                    .run(connection);

            var values = await Future.wait([f1, f2, f3]);
            connection.close();
            var counters = values[2];

            return {
                'url': 'https://news.ycombinator.com/item?id=${MAIN_ID}',
                'date': values[1]['time'],
                'latest': values[0]['time'],
                'liked': counters[2],
                'disliked': counters[0],
                'unclassified': counters[1],
                'total': counters.values.fold(0, (a, b) => a+b)
            };
        });

main() {

    app.setShelfHandler(createStaticHandler('../../public', defaultDocument: 'index.html'));

    //RethinkdbManager manager = new RethinkdbManager('localhost', 'hnjobs');
    //app.addPlugin(rethinkPlugin(manager));

    app.setupConsoleLog();
    app.start(port:3000);
}
