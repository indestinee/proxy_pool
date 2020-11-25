import unittest
import checker

class TestChecker(unittest.TestCase):

    def test_get_proxies(self):
        raw = '0.0.0.0:1\n255.255.255.255:65535\nasd'
        raw_1 = ['12.1.1.2:23', '123.231.0.1:112 ', 'a', 'zcx']
        self.assertEqual(
                ['0.0.0.0:1', '255.255.255.255:65535'],
                checker.get_proxies(raw))
        self.assertEqual(
                ['12.1.1.2:23', '123.231.0.1:112'],
                checker.get_proxies(raw_1))


if __name__ == '__main__':
    unittest.main()
