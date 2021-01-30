import itertools
import requests
import threading
import time

from concurrent.futures import ThreadPoolExecutor

import config
import sqls
import ip_fetcher


class ProxyPool:
    def __init__(self, db_client, sess, logger, proxy_pool_client):
        self.sess = sess
        self.db_client = db_client
        self.logger = logger
        self.db_client.execute(sqls.CREATE_TABLE_SQLS)
        self.proxy_pool_client = proxy_pool_client
        self.fetch_lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)

    def get_proxies(self, num, caller, ignore_freeze):
        return [
            item[0] for item in
            self.db_client.execute(sqls.RANDOM_PICK_SQL, [caller, time.time() + (1e18 if ignore_freeze else 0), num])
        ]

    def add_proxies(self, proxies):
        if proxies:
            sql = sqls.INSERT_PROXY_SQL.format(', '.join(['(?, ?, ?)'] * len(proxies)))
            params = [[proxy, sqls.Active.unknown, 0] for proxy in proxies]
            self.db_client.execute(sql, list(itertools.chain(*params)))

    def freeze_proxy(self, proxies, caller, second):
        if proxies:
            self.db_client.execute(
                sqls.INSERT_STATUS_SQL.format(', '.join(['?'] * len(proxies))),
                [time.time() + second, caller, *proxies])

    def proxy_status(self):
        return self.db_client.execute(sqls.QUERY_PROXY_STATUS_SQL)

    def reset_proxy(self, active):
        return self.db_client.execute(sqls.RESET_PROXY_SQLS, [active, active])

    def add_caller(self, caller):
        return self.db_client.execute(sqls.INSERT_CALLER_SQL, [caller])

    def fetch_proxy(self, page):
        if self.fetch_lock.acquire(blocking=True, timeout=0):
            try:
                ip_fetcher.run_fetch_proxy(page, self.proxy_pool_client, self.logger)
                return ''
            finally:
                self.fetch_lock.release()
        return 'fetching proxy is already in progress.'

    def update_proxy(self, indices, active):
        indices = ', '.join(map(str, indices))
        self.db_client.execute(sqls.UPDATE_ACTIVE_SQL.format(indices), [active, time.time()])

    def is_alive(self, index, proxy):
        try:
            proxies = {'https': 'https://' + proxy, 'http': 'http://' + proxy}
            response = self.sess.get(
                config.TEST_URL, proxies=proxies, timeout=config.TIMEOUT)
            return [True, index] if response else [False, index]
        except requests.exceptions.ConnectionError:
            return False, index
        except Exception as e:
            self.logger.print_exception()
            return False, index

    def search_survivors(self, proxies):
        futures = [self.executor.submit(self.is_alive, index=proxy[0], proxy=proxy[1]) for proxy in proxies]
        return [future.result() for future in futures]

    def maintenance_proxies(self, active, update_time=time.time() - config.EXPIRED_TIME):
        self.logger.info('start check type {} proxies'.format(active))
        proxies = self.db_client.execute(sqls.SELECT_PROXY_SQL, [update_time, active, config.BATCH_SIZE])
        survivors = self.search_survivors(proxies)
        successful_results = [survivor[1] for survivor in survivors if survivor[0]]
        failed_results = [survivor[1] for survivor in survivors if not survivor[0]]
        self.update_proxy(successful_results, sqls.Active.active)
        self.update_proxy(failed_results, sqls.Active.inactive)
        self.logger.info(
            'type {}: {} => active, {} => inactive'.format(active, len(successful_results), len(failed_results)))
        return len(proxies)

    def schedule_fetch_proxy(self, page, sleep_time):
        while True:
            start_time = time.time()
            try:
                self.fetch_proxy(page)
            except Exception as e:
                self.logger.print_exception()
            time.sleep(max(0.0, sleep_time - (time.time() - start_time)))

    def maintenance(self, active, sleep_time):
        cnt = 0
        while True:
            cnt += 1
            try:
                if self.maintenance_proxies(active) < config.BATCH_SIZE:
                    time.sleep(sleep_time)
                if cnt % 5 == 0:
                    self.reset_proxy(sqls.Active.inactive)
            except Exception as e:
                self.logger.print_exception()

    def start_maintenance(self):
        self.executor.submit(self.maintenance, active=sqls.Active.active, sleep_time=config.ACTIVE_SLEEP_TIME)
        self.executor.submit(self.maintenance, active=sqls.Active.inactive, sleep_time=config.INACTIVE_SLEEP_TIME)
        self.executor.submit(self.maintenance, active=sqls.Active.unknown, sleep_time=config.UNKNOWN_SLEEP_TIME)
        self.executor.submit(self.schedule_fetch_proxy, page=config.FETCH_PAGE_NUM, sleep_time=config.FETCH_SLEEP_TIME)
