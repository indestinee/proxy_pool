import logging
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


class Modules:
    def __init__(self, args):
        sess = requests.Session()
        sess.mount('https://', HTTPAdapter(max_retries=Retry(total=3)))
        database_client = DB_CLIENTS[args.db](config.DB_NAME)
        self.logger = ColorfulLog(LOG_LEVELS[args.level], log_name='proxy_pool')
        self.proxy_pool_client = Client(caller='proxy_pool', host=args.host, port=args.port)
        self.proxy_pool = ProxyPool(database_client, sess, self.logger, self.proxy_pool_client)

    def run(self):
        self.proxy_pool.start_maintenance()
