#! /bin/sh
uwsgi --http :5000 --gevent 1000 --http-websockets --master --wsgi-file socket_demo.py --callable app