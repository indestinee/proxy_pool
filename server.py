import os

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

import checker
import config
import modules

assert __name__ == '__main__'

proxy_pool_modules = modules.Modules(modules.get_args())

app = Flask('proxy_pool', static_folder='static', static_url_path='/static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logs')
@app.route('/logs/<string:fn>')
def get_logs(fn=''):
    fn = os.path.join(config.LOG_PATH, os.path.basename(fn))
    if os.path.isfile(fn) and fn.endswith('.log'):
        with open(fn) as f:
            return '\n'.join(map('<p>{}</p>'.format, f.readlines()))
    logs = sorted(os.listdir(config.LOG_PATH))
    return '\n'.join(['<p><a href="/logs/{log}">{log}</a></p>'.format(log=log) for log in logs])


@app.route('/get_proxy', methods=['POST'])
def get_proxy():
    try:
        data = request.get_json()
        num = checker.get_pos_int(data['num'])
        caller = checker.get_non_empty_str(data['caller'])
        second = checker.get_natural_int(data['freeze_time'])
        ignore_freeze = bool(data['ignore_freeze'])
        proxy_pool_modules.proxy_pool.add_caller(caller)
        proxies = proxy_pool_modules.proxy_pool.get_proxies(num, caller, ignore_freeze)
        if second:
            proxy_pool_modules.proxy_pool.freeze_proxy(proxies, caller, second)
        return jsonify({'success': True, 'error_msg': '', 'proxies': proxies})
    except Exception as e:
        proxy_pool_modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e), 'proxies': []})


@app.route('/add_proxy', methods=['POST'])
def add_proxy():
    try:
        data = request.get_json()
        proxies = checker.get_proxies(data['proxies'])
        proxy_pool_modules.proxy_pool.add_proxies(proxies)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        proxy_pool_modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/freeze_proxy', methods=['POST'])
def freeze_proxy():
    try:
        data = request.get_json()
        proxies = checker.get_proxies(data['proxies'])
        caller = checker.get_non_empty_str(data['caller'])
        second = checker.get_natural_int(data['second'])
        proxy_pool_modules.proxy_pool.add_caller(caller)
        proxy_pool_modules.proxy_pool.freeze_proxy(proxies, caller, second)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        proxy_pool_modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/proxy_status', methods=['GET'])
def proxy_status():
    try:
        status = proxy_pool_modules.proxy_pool.proxy_status()
        return jsonify({'success': True, 'error_msg': '', 'status': status})
    except Exception as e:
        proxy_pool_modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e), 'status': []})


@app.route('/reset_proxy', methods=['GET'])
@app.route('/reset_proxy/<int:active>', methods=['GET'])
def reset_proxy(active=1):
    try:
        proxy_pool_modules.proxy_pool.reset_proxy(active)
        return jsonify({'success': True, 'error_msg': ''})
    except Exception as e:
        proxy_pool_modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


@app.route('/update_proxy', methods=['GET'])
@app.route('/update_proxy/<int:page>', methods=['GET'])
def update_proxy(page=5):
    try:
        msg = proxy_pool_modules.proxy_pool.fetch_proxy(page)
        return jsonify({'success': False if msg else True, 'error_msg': msg})
    except Exception as e:
        proxy_pool_modules.logger.print_exception()
        return jsonify({'success': False, 'error_msg': str(e)})


proxy_pool_modules.run()
app.run(host=proxy_pool_modules.args.host, port=proxy_pool_modules.args.port, debug=proxy_pool_modules.args.debug)
