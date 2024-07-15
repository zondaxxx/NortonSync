import psutil
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/server_stats')
def server_stats():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    return jsonify(cpu=cpu, memory=memory, disk=disk)

@app.route('/message_stats')
def message_stats():
    # функ для статистики сообщений
    return jsonify(messages_sent=1234, messages_received=5678)

@app.route('/user_list')
def user_list():
    # функ для юзеров бота
    users = ["user1", "user2", "user3"]
    return jsonify(users=users)

@app.route('/groups')
def groups():
    # функ для групп
    groups = ["group1", "group2", "group3"]
    return jsonify(groups=groups)

if __name__ == '__main__':
    socketio.run(app, debug=True)