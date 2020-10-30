import requests

from proxy_pool import config


class Client:
    def __init__(self, caller, host='127.0.0.1', port=23301):
        self.sess = requests.Session()
        self.url = 'http://{}:{}'.format(host, port)
        self.caller = caller

    def get_proxy(self, num=1, ignore_freeze=False, freeze_time=config.DEFAULT_FREEZE_PROXY_TIME, caller=None):
        if caller is None:
            caller = self.caller
        return requests.post('{}/get_proxy'.format(self.url),
                             json={'num': num, 'caller': caller, 'ignore_freeze': ignore_freeze,
                                   'freeze_time': freeze_time}).json()

    def add_proxy(self, proxies):
        return requests.post('{}/add_proxy'.format(self.url), json={'proxies': proxies}).json()

    def freeze_proxy(self, proxies, second=config.DEFAULT_FREEZE_BAD_PROXY_TIME, caller=None):
        if caller is None:
            caller = self.caller
        return requests.post('{}/freeze_proxy'.format(self.url),
                             json={'proxies': proxies, 'second': second, 'caller': caller}).json()
