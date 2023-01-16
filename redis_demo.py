import json
import time
import gevent.monkey
import redis.client

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
REDIS_HOST = "localhost"
REDIS_PORT = 6379
redis_client = Redis(host='localhost', port=REDIS_PORT)


@app.route('/')
def index():
    emit("Some thing")
    return render_template('index.html')


@socketio.on('connect')
def test_connect():
    print('client connected')
    emit('after connect', {'data': 'Lets dance'})


@socketio.on("push_progress")
def update_progress(data):
    """
    Update progress for a wall
    {
        "wall_id":1,
        "progress":100
    }
    :param message:
    :return:
    """
    try:
        wall_id = data.get('wall_id')
        progress = int(data.get('progress'))
        print('progress udate: {}'.format(progress))
        redis_client.publish(wall_id, progress)
    except Exception as e:
        print('error on push progress')
        print(e)


@socketio.on('subscribe')
def subscribe(data):
    """
    Call from client
    :param data:
    :param message:
    :return:
    """
    ""
    try:
        print('subscribe: {}'.format(data))
        token = data.get("token")
        wall_id = data.get("wall_id")
        if not token:
            raise Exception("Invalid token")
        if not wall_id:
            raise Exception("Invalid wall_id")
    except Exception as e:
        print("Wrong format data")
        return
    token = data.get("token")
    ok = validate_session_token(token)
    if not ok:
        print("Invalid session token")
        return

    pub = redis_client.pubsub()
    pub.subscribe(wall_id)
    while True:
        socketio.sleep(0.1)
        message = get_redis_message(pub)
        if message:
            print('message in pub: {}'.format(message))
            emit('progress_update', message)
    # for message in pub.listen():
    #     print('message in pub: {}'.format(message))
    #     if message:
    #         emit('progress_update', message)


@app.route('/generate_token')
def generate_token():
    """
    Generate a valid token, and save it to redis data
    :return:
    """
    token = generate_random_token()
    success = save_value_key(token, "ok")
    return {'success': success, 'token': token}


def get_redis_message(pub):
    data = pub.get_message()
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
        print('write redis failed')
        print(e)
        return False


def get_value_key(key):
    try:
        data = redis_client.get(key)
        return data
    except Exception as e:
        return None


def generate_random_token():
    from uuid import uuid4
    rand_token = str(uuid4())
    return rand_token


def validate_session_token(token):
    data = get_value_key(token)
    print(data)
    if data:
        return True
    return False


if __name__ == '__main__':
    print('run socket server')
    socketio.run(app, host='0.0.0.0', port='5000')
