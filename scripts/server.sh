#!/bin/sh

cd `dirname ${0}`/../

source bootstrap_venv/bin/activate

./server.py
