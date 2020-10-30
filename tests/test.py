import unittest

from client import Client


class TestServer(unittest.TestCase):
    client = Client(caller="test")
    proxy = "1234"

    def test(self):
        self.client.add_proxy(self.proxy)
        self.client.freeze_proxy(self.proxy)


if __name__ == '__main__':
    unittest.main()
