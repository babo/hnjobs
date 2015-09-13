import 'package:rethinkdb_driver/rethinkdb_driver.dart';
import 'dart:async';

final Rethinkdb r = new Rethinkdb();

final String MAIN_ID = '9471287';
final LIMIT = 700;
final DB_HOST = 'localhost';
final DB_PORT = 28015;
final DB_DATABASE = 'hnjobs';

main2() async {
    await r.connect(db: DB_DATABASE, port: DB_PORT, host: DB_HOST)
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
            return values[2];
        })
        .then((latest) => print('Hello dart ${latest}'));

    print('Itt a vege.');
}

main() async {
    var ize = await r.connect(db: DB_DATABASE, port: DB_PORT, host: DB_HOST)
        .then((connection) async {
            var cursor =  await r.table(MAIN_ID)
                .filter(r.row('parent').eq(int.parse(MAIN_ID)))
                .filter(r.row('type').eq('comment'))
                .limit(LIMIT)
                .withFields(['text', 'by', 'time', 'cool', 'id'])
                .run(connection)
                .then((cursor) {
                    return cursor.toArray().then((x) {
                        print(x);
                        return x;
                        });
                });
            connection.close();
            return cursor;
        });
    print(ize);
    print('vege');
}

main0() async {
    var ize = await r.connect(db: DB_DATABASE, port: DB_PORT, host: DB_HOST)
        .then((connection) async {
            var rtv2 = r.table(MAIN_ID)
                .filter(r.row('parent').eq(int.parse(MAIN_ID)))
                .filter(r.row('type').eq('comment'))
                .limit(LIMIT)
                .withFields(['text', 'by', 'time', 'cool', 'id'])
                .run(connection)
                .then((cursor) => cursor.toArray())
                .then((x) => x);
            var rtv = await Future.wait([rtv2]);
            connection.close();
            print(rtv);
            return rtv;
        })
        .catchError((err) {
            print(err);
            return [];
        });
    print(ize);
}
