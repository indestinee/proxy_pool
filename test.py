import requests

url = 'http://127.0.0.1:23301'
sess = requests.Session()


def add_proxy_test():
    response = sess.post(
        '{}/add_proxy'.format(url), json={'proxies': ['127.0.0.1:1234']})
    assert response.json()['success']
    response = sess.post('{}/add_proxy'.format(url), json={'proxies': 1234})
    assert not response.json()['success']


def get_proxy_test():
    response = sess.post('{}/get_proxy'.format(url), json={'num': 1})
    assert response.json()['success'] and response.json()['proxies']


def freeze_proxy_test():
    response = sess.post('{}/freeze_proxy'.format(url), json={'indices', [1]})
    assert response.json()['success']


def test():
    add_proxy_test()
    get_proxy_test()


if __name__ == '__main__':
    test()
