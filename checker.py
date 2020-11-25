import re

PROXY_PATTERN = re.compile('^(\d{1,3}\.){3}\d{1,3}:[\d]{1,5}$')


def get_non_empty_str(value):
    value = str(value)
    assert len(value) > 0
    return value


def get_pos_int(value):
    value = int(value)
    assert value > 0
    return value


def get_natural_int(value):
    value = int(value)
    assert value >= 0
    return value


def get_proxy(row):
    row = row.strip()
    return row if PROXY_PATTERN.match(row) else None


def get_proxies(rows):
    if isinstance(rows, str):
        rows = rows.split('\n')
    return [proxy for proxy in map(get_proxy, rows) if proxy]
