import time
import gevent.monkey

gevent.monkey.patch_all()
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room
from flask_socketio import send, emit
import gevent
from redis import Redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
values = {
    'slider1': 25,
    'slider2': 0,
}
REDIS_HOST = "redis"
REDIS_PORT = 6379
redis_client = Redis(host='redis', port=6379)


@app.route('/')
def index():
    emit("Some thing")
    return render_template('index.html')


@socketio.on('connect')
def test_connect():
    print('client connected')
    emit('after connect', {'data': 'Lets dance'})


@socketio.on('subscribe/<token_id>/<wall_id>')
def subscribe(message):
    print('event come: {}'.format(message))
    count = 0
    while (True):
        count += 1
        socketio.sleep(0.1)
        if count > 100:
            return
        result = {"progress": count}
        print(f'emit progress: {count}')
        emit('progress_update', result)


@app.route('generate_token')
def generate_token():
    """
    Generate a valid token, and save it to redis data
    :return:
    """
    token = generate_random_token()
    success = save_value_key(token, "ok")
    return {'success': success, 'token': token}


def get_redis_message(pub):
    data = pub_item.get_message()
    LOG.info(data)
    if data:
        message = data['data']
        if message and message != 1:
            return message
    return None


def save_value_key(key, data, ttl=1000000):
    try:
        redis_client.set(key, data, ttl)
        return True
    except Exception as e:
        return False


def generate_random_token():
    from uuid import uuid4
    rand_token = str(uuid4())
    return rand_token


if __name__ == '__main__':
    print('run socket server')
    socketio.run(app, host='0.0.0.0', port='5000')
