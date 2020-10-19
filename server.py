import argparse

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from healthcheck import HealthCheck

import modules

assert __name__ == '__main__'


def get_args():
    parser = argparse.ArgumentParser(description='Proxy Pool')
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default='23301', type=str)
    parser.add_argument('--db', default='sqlite3', type=str, choices=modules.DB_CLIENTS)
    parser.add_argument('--level', default='debug', type=str, choices=modules.LOG_LEVELS)
    return parser.parse_args()


args = get_args()
modules = modules.Modules(args)

app = Flask('proxy_pool', static_folder='static', static_url_path='/static')
health = HealthCheck(app, '/healthcheck')
health.add_check(lambda: [True, 1])


@app.route('/')
def index():
    return redirect('healthcheck')


@app.route('/get_proxy', methods=['POST'])
def get_proxy():
    data = request.get_json()
    num = data['num']
    try:
        proxies = modules.proxy_pool.get_proxies(num)
        return jsonify({'success': True, 'error_msg': '', 'proxies': proxies})
    except Exception as e:
        return jsonify({'success': False, 'error_msg': str(e), 'proxies': []})


@app.route('/add_proxy', methods=['POST'])
def add_proxy():
    data = request.get_json()
    proxies = data['proxies']
    try:
        modules.proxy_pool.add_proxies(proxies)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/freeze_proxy', methods=['POST'])
def freeze_proxy():
    data = request.get_json()
    indices = data['indices']
    try:
        modules.proxy_pool.freeze_proxy(indices)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/submit_proxy', methods=['GET'])
def submit_proxy():
    return render_template('submit_proxy.html')


modules.run()
app.run(host=args.host, port=args.port)
