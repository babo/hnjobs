#!/bin/sh

# A script to start hnjobs within a tmux session, all 3 components:
# - hn.py: The scraper and fills in the DB
# - rethinkdb: The database itself, with it's data stored in db/
# - server.py: The web app component that the user interacts with

cd `dirname ${0}`/../

sess_name="hnjobs"

tmux -2 new-session -d -s $sess_name -n 'scraping' "scripts/scrape.sh"
tmux new-window -t $sess_name:1 -n 'db' "rethinkdb -d db/"
tmux new-window -t $sess_name:2 -n 'server' "scripts/server.sh"

tmux select-window -t $sess_name:2

exec tmux -2 attach -d -c "$(pwd)" -t $sess_name
