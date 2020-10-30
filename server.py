import argparse

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

import checker
import modules

assert __name__ == '__main__'


def get_args():
    parser = argparse.ArgumentParser(description='Proxy Pool')
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=23301, type=int)
    parser.add_argument('--db', default='sqlite3', type=str, choices=modules.DB_CLIENTS)
    parser.add_argument('--level', default='debug', type=str, choices=modules.LOG_LEVELS)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


args = get_args()
modules = modules.Modules(args)

app = Flask('proxy_pool', static_folder='static', static_url_path='/static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_proxy', methods=['POST'])
def get_proxy():
    try:
        data = request.get_json()
        num, caller, second, ignore_freeze = [
            int(data['num']), data['caller'], int(data['freeze_time']), bool(data['ignore_freeze'])]
        checker.check_caller(caller)
        checker.check_pos_int(num)
        modules.proxy_pool.add_caller(caller)
        proxies = modules.proxy_pool.get_proxies(num, caller, ignore_freeze)
        if caller and second > 0:
            modules.proxy_pool.freeze_proxy(proxies, caller, second)
        return jsonify({'success': True, 'error_msg': '', 'proxies': proxies})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e), 'proxies': []})


@app.route('/add_proxy', methods=['POST'])
def add_proxy():
    try:
        data = request.get_json()
        proxies = data['proxies']
        modules.proxy_pool.add_proxies(proxies)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/freeze_proxy', methods=['POST'])
def freeze_proxy():
    try:
        data = request.get_json()
        proxies, caller, second = data['proxies'], data['caller'], data['second']
        checker.check_caller(caller)
        modules.proxy_pool.add_caller(caller)
        modules.proxy_pool.freeze_proxy(proxies, caller, second)
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
app.run(host=args.host, port=args.port, debug=args.debug)
