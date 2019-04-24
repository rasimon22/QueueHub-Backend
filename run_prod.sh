#!/usr/bin/env bash
gunicorn app:app -c gunicorn.py.ini --worker-class gevent --bind 0.0.0.0:8000&
disown
