#!/bin/sh

# An infinite loop, just runs the hn.py scraper once an hour (ish)

cd `dirname ${0}`/../

source bootstrap_venv/bin/activate

while : ; do
  sleep 10 # since the script starts at the same time as the db, give rethinkdb
           # a chance to finish loading first
  ./hn.py
  printf "\x1b[32mFinished latest post grab!\x1b[0m"
  sleep 1h
done
