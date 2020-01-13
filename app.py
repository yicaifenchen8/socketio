import psutil
import time
from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO()
socketio.init_app(app)


thread = None

thread_lock = Lock()


# 后台线程 产生数据，即刻推送至前端

def background_thread():
    count = 0

    while True:
        socketio.sleep(5)

        count += 1

        t = time.strftime('%M:%S', time.localtime())

        # 获取系统时间（只取分:秒）

        cpus = psutil.cpu_percent(interval=None, percpu=True)

        # 获取系统cpu使用率 non-blocking

        socketio.emit('server_response',

                      {'data': [t, cpus], 'count': count},

                      namespace='/test')

        socketio.emit('messageEventNew',

                      {'encryptkey':'key'},

                      namespace='/test')

        # 注意：这里不需要客户端连接的上下文，默认 broadcast = True


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/test')
def test_connect():
    print('connect')
    global thread

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)

@socketio.on('onMessageArrive', namespace='/test')
def test_connect():
    print('onMessageArrive')

if __name__ == '__main__':
    # 只能点击main运行，flask项目修改不了host，新增pure项目拷贝代码即可
    socketio.run(app, host='10.10.9.74', port=5000, debug=True)

