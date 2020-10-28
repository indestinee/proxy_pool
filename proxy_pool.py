import itertools
import requests
import sys
import threading
import time

from concurrent.futures import ThreadPoolExecutor

import config
import sqls
from ip_fetcher import schedule_fetch_proxy


class ProxyPool:
    def __init__(self, db_client, sess, logger, proxy_pool_client):
        self.sess = sess
        self.db_client = db_client
        self.logger = logger
        self.db_client.execute(sqls.CREATE_TABLE_SQL)
        self.proxy_pool_client = proxy_pool_client

    def get_proxies(self, num):
        return self.db_client.execute(sqls.RANDOM_PICK_SQL, [num])

    def add_proxies(self, proxies):
        if isinstance(proxies, str):
            proxies = [proxy.strip() for proxy in proxies.split('\n') if proxy.strip()]
        elif isinstance(proxies, list):
            pass
        else:
            raise NotImplementedError(
                'type {} not implement in ProxyPool/add_proxies'.format(type(proxies)))
        if proxies:
            sql = sqls.INSERT_PROXY_SQL.format(', '.join(['(?, ?, ?)'] * len(proxies)))
            params = [[proxy, sqls.Active.unknown, 0] for proxy in proxies]
            self.db_client.execute(sql, list(itertools.chain(*params)))

    def freeze_proxy(self, indices):
        if isinstance(indices, int):
            indices = [indices]
        elif isinstance(indices, list):
            pass
        else:
            raise NotImplementedError(
                'type {} not implement in ProxyPool/freeze_proxy'.format(type(indices)))
        if indices:
            self.db_client.execute(
                sqls.UPDATE_ACTIVE_SQL.format(', '.join(['?'] * len(indices))),
                [sqls.Active.unknown, time.time(), *indices])

    def proxy_status(self):
        return self.db_client.execute(sqls.QUERY_PROXY_STATUS_SQL)

    def reset_proxy(self, active):
        return self.db_client.execute(sqls.RESET_PROXY_SQL, [active])

    def fetch_proxy(self, page):
        return schedule_fetch_proxy(page, self.proxy_pool_client, self.logger)

    def update_proxy(self, indices, active):
        indices = ', '.join(map(str, indices))
        self.db_client.execute(
            sqls.UPDATE_ACTIVE_SQL.format(indices), [active, time.time()])

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
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.is_alive, index=proxy[0], proxy=proxy[1])
                for proxy in proxies]
            executor.shutdown(wait=True)
        return [future.result() for future in futures]

    def maintenance_execution(self, active, update_time=time.time() - config.EXPIRED_TIME):
        self.logger.info('start check type {} proxies'.format(active))
        proxies = self.db_client.execute(sqls.SELECT_PROXY_SQL, [update_time, active])
        results = self.search_survivors(proxies)
        successful_results = [result[1] for result in results if result[0]]
        failed_results = [result[1] for result in results if not result[0]]
        self.update_proxy(successful_results, sqls.Active.active)
        self.update_proxy(failed_results, sqls.Active.inactive)
        self.logger.info(
            'type {}: {} => active, {} => inactive'.format(active, len(successful_results), len(failed_results)))

    def maintenance(self, active, sleep_time):
        while True:
            try:
                self.maintenance_execution(active)
            except Exception as e:
                self.logger.print_exception()
            finally:
                time.sleep(sleep_time)

    def start_maintenance(self):
        params = [
            [sqls.Active.active, config.ACTIVE_SLEEP_TIME],
            [sqls.Active.inactive, config.INACTIVE_SLEEP_TIME],
            [sqls.Active.unknown, config.UNKNOWN_SLEEP_TIME]]
        threads = [
            threading.Thread(target=self.maintenance, args=param)
            for param in params]
        for thread in threads:
            thread.start()
