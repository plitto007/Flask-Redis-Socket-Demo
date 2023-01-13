import time

import flask
import requests
from flask import Flask, Response, stream_with_context

app = Flask(__name__)


@app.route("/foo")
def foo():
    _resp = requests.get("https://speed.hetzner.de/100MB.bin", stream=True)
    _resp.raise_for_status()

    resp = Response(
        response=stream_with_context(_resp.iter_content(chunk_size=1024 * 10)),
        status=200,
        content_type=_resp.headers["Content-Type"],
        direct_passthrough=False)
    return resp


@app.route('/wall_progress/<wall_id>')
def wall_progress(wall_id):
    try:
        def update():
            yield 'data: Prepare for learning\n\n'
            # Preapre model
            time.sleep(1.0)

            for i in range(1, 101):
                # Perform update
                time.sleep(0.1)
                temp = {"wall_id": wall_id, "progress": i}
                yield f'{temp}%\n'

            yield 'data: close\n\n'

        return flask.Response(update(), mimetype='text/event-stream')
    except Exception as e:
        print('error: {}'.format(e))


@app.route('/learn/<wall_id>')
def learn(wall_id):
    try:
        def update():
            yield 'response: Prepare for learning\n\n'
            # Preapre model
            time.sleep(1.0)
            _resp = requests.get("http://localhost:1234/wall_progress/{}".format(wall_id), stream=True)
            for line in _resp.iter_lines():
                print('progress: {}'.format(line))
                yield f'response: {line}\n'
            #
            # for i in range(1, 101):
            #     # Perform update
            #     time.sleep(0.1)
            #     print('data: {}'.format(i))
            #     yield f'data: {i}%\n\n'
            #
            yield 'data: close\n\n'

        return flask.Response(update(), mimetype='text/event-stream')
    except Exception as e:
        print('error: {}'.format(e))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1234)
