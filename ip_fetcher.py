import argparse
import re
import time

from lxml import etree

from client import Client
from fetcher.config import CONFIGS

RE_TAGS = re.compile(r'<[^>]+>')
RE_IGNORE = re.compile(r'[ \t\n\r]')
PATTERN = re.compile(r'(\d+\.\d+\.\d+\.\d+) *:* *(\d+)')


def get_args():
    parser = argparse.ArgumentParser(description='proxies_fetcher.')
    parser.add_argument('-p', '--page', default=2, type=int)
    parser.add_argument(
        '-s', '--site', default='kuaidaili', type=str, choices=CONFIGS.keys())
    return parser.parse_args()


def fetch(url, sess):
    response = sess.get(url)
    return response.text


def parse(html, xpath):
    page = etree.HTML(html)
    items = page.xpath(xpath)
    res = []
    for item in items:
        text = etree.tostring(item, method='html').decode('utf-8')
        text = RE_TAGS.sub('', text)
        text = RE_IGNORE.sub(' ', text)
        results = PATTERN.findall(text)
        for result in results:
            if result and len(result) == 2:
                res.append('{}:{}'.format(*result))
    return res


def main():
    args = get_args()
    config = CONFIGS[args.site]
    client = Client()
    sess = config['sess']
    xpath = config['xpath']
    url = config['url']
    for i in range(1, args.page + 1):
        html = fetch(url.format(page_id=i), sess)
        proxies = parse(html, xpath)
        print('len:', len(proxies))
        response = client.add_proxy(proxies)
        print(response)
        time.sleep(1)


if __name__ == '__main__':
    main()
