import time
import gevent.monkey
gevent.monkey.patch_all()
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room
from flask_socketio import send, emit
import gevent
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")
values = {
    'slider1': 25,
    'slider2': 0,
}


@app.route('/')
def index():
    emit("Some thing")
    return render_template('index.html')


@socketio.on('connect')
def test_connect():
    print('client connected')
    emit('after connect', {'data': 'Lets dance'})


@socketio.on('subscribe')
def value_changed(message):
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


if __name__ == '__main__':
    print('run socket server')
    socketio.run(app, host='0.0.0.0', port='5000')
