Organize monthly Hacker News jobs
==

Description
--

[Ask HN: Who is hiring?](https://news.ycombinator.com/item?id=8252715) at the first day of each month at 9 AM Eastern time is a great source of jobs and trends in the startup world. Following it is quite a hassle as the UI is not designed for hundreds of posts in a single page. This application is cloning it into a local database and adds a UI to select interesting jobs and hide the unattractive ones.

Requirements
---

    python3
    virtualenv

Installation
---

The current database is [RethinkDB](http://rethinkdb.com/docs/install/), use they instructions to install it. On OS X with [brew](http://brew.sh/) it's as easy as:

    brew update && brew install --upgrade rethinkdb

Backend is written in python using a minimalistic approach with [flask](http://flask.pocoo.org/). To run it use `setup.sh` to create a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) with the required packages installed in it.

Frontend is using [ReactJS](https://facebook.github.io/react/), [jquery](http://jquery.com) and [bootstrap](http://getbootstrap.com/) with on the fly [JSX](http://facebook.github.io/jsx/) transformation.

Starting the service
---

* start your database somewhere with `rethinkdb -d YOUR_PREFERRED_DATABASE_DIRECTORY_LOCATION`.

* activate the virtualenv with `source ./bootstrap_venv/bin/activate`

* run `./hn.py` to collect data using [firebaseio.com](http://hacker-news.firebaseio.com). This will take around 10 minutes. At the first days of the month you should run this frequently to collect the latest jobs and comments.

* start the local server as `./server.py` and point your browser to `http://localhost:3000`. To run it on a different port use `env PORT=XXXX ./server.py`

Stopping the service
--

* stop `server.py` with a `CTRL-C`
* stop `rethinkdb` with a `CTRL-C`
