import json
import re
import requests
import time

from lxml import etree

RE_TAGS = re.compile(r'<[^>]+>')
RE_IGNORE = re.compile(r'[ \t\n\r]')
PATTERN = re.compile(r'(\d+\.\d+\.\d+\.\d+) *:* *(\d+)')


def get_default_session():
    sess = requests.Session()
    sess.headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    return sess


def fetch(url, sess, logger):
    logger.info(url)
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


def schedule_fetch_proxy(num, client, logger):
    with open("fetcher_config.json", "r") as f:
        configs = json.load(f)
    for config in configs.values():
        sess = get_default_session()
        xpath = config['xpath']
        url = config['url']
        page = num if '{page_id}' in url else 1
        for i in range(1, page + 1):
            html = fetch(url.format(page_id=i), sess, logger)
            proxies = parse(html, xpath)
            response = client.add_proxy(proxies)
            logger.info(response)
            time.sleep(1)
