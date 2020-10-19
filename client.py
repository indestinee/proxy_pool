import requests


class Client:
    def __init__(self, host='127.0.0.1', port=23301):
        self.sess = requests.Session()
        self.url = 'http://{}:{}'.format(host, port)

    def get_proxy(self, num=1):
        return requests.post('{}/get_proxy'.format(self.url), json={'num': num}).json()

    def add_proxy(self, proxies):
        return requests.post('{}/add_proxy'.format(self.url), json={'proxies': proxies}).json()

    def freeze_proxy(self, indices):
        return requests.post('{}/freeze_proxy'.format(self.url), json={'indices': indices}).json()
