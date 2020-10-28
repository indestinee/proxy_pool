import argparse

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_proxy', methods=['POST'])
def get_proxy():
    data = request.get_json()
    num = data['num']
    try:
        proxies = modules.proxy_pool.get_proxies(num)
        return jsonify({'success': True, 'error_msg': '', 'proxies': proxies})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e), 'proxies': []})


@app.route('/add_proxy', methods=['POST'])
def add_proxy():
    data = request.get_json()
    proxies = data['proxies']
    try:
        modules.proxy_pool.add_proxies(proxies)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/freeze_proxy', methods=['POST'])
def freeze_proxy():
    data = request.get_json()
    indices = data['indices']
    try:
        modules.proxy_pool.freeze_proxy(indices)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/proxy_status', methods=['GET'])
def proxy_status():
    try:
        status = modules.proxy_pool.proxy_status()
        return jsonify({'success': True, 'error_msg': '', 'status': status})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e), 'status': []})


@app.route('/reset_proxy', methods=['GET'])
@app.route('/reset_proxy/<int:active>', methods=['GET'])
def reset_proxy(active=1):
    try:
        modules.proxy_pool.reset_proxy(active)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/fetch_proxy', methods=['GET'])
@app.route('/fetch_proxy/<int:page>', methods=['GET'])
def update_proxy(page=5):
    try:
        modules.proxy_pool.fetch_proxy(page)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


modules.run()
app.run(host=args.host, port=args.port)
