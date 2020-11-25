import requests

from proxy_pool import config


class Client:
    def __init__(self, caller, protocol='http', host='127.0.0.1', port=23301):
        self.sess = requests.Session()
        self.caller = caller
        self.url = '{}://{}:{}'.format(protocol, host, port)

    def get_proxy(self, num=1, ignore_freeze=False, freeze_second=config.DEFAULT_FREEZE_PROXY_TIME):
        return requests.post(
            '{}/get_proxy'.format(self.url),
            json={'num': num, 'caller': self.caller, 'ignore_freeze': ignore_freeze, 'freeze_second': freeze_second}
        ).json()

    def add_proxy(self, proxies):
        return requests.post(
            '{}/add_proxy'.format(self.url), json={'proxies': proxies}
        ).json()

    def freeze_proxy(self, proxies, freeze_second=config.DEFAULT_FREEZE_BAD_PROXY_TIME):
        return requests.post(
            '{}/freeze_proxy'.format(self.url),
            json={'proxies': proxies, 'freeze_second': freeze_second, 'caller': self.caller}
        ).json()

    def update_proxy(self):
        return requests.get(
            '{}/update_proxy'.format(self.url)
        ).json()
