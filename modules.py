import argparse
import logging
import time

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util import Retry

import config
from ec_tools.database.sqlite_client import SqliteClient
from ec_tools import ColorfulLog

from client import Client
from proxy_pool import ProxyPool

DB_CLIENTS = {'sqlite3': SqliteClient}
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warn': logging.WARN,
    'error': logging.ERROR,
}


def get_args():
    parser = argparse.ArgumentParser(description='Proxy Pool')
    parser.add_argument('--host', default='127.0.0.1', type=str)
    parser.add_argument('--port', default=23301, type=int)
    parser.add_argument('--db', default='sqlite3', type=str, choices=DB_CLIENTS)
    parser.add_argument('--level', default='debug', type=str, choices=LOG_LEVELS)
    parser.add_argument('--debug', action='store_true')
    return parser.parse_args()


class Modules:
    def __init__(self, args):
        sess = requests.Session()
        sess.mount('https://', HTTPAdapter(max_retries=Retry(total=3)))
        database_client = DB_CLIENTS[args.db](config.DB_NAME)
        log_name = time.strftime('proxy_pool_%Y%m%d_%H%M%S')
        self.args = args
        self.logger = ColorfulLog(LOG_LEVELS[args.level], log_dir=config.LOG_PATH, log_name=log_name)
        self.proxy_pool_client = Client(caller='proxy_pool', host=args.host, port=args.port)
        self.proxy_pool = ProxyPool(database_client, sess, self.logger, self.proxy_pool_client)

    def run(self):
        self.proxy_pool.start_maintenance()
