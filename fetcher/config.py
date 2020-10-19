from fetcher import sessions

CONFIGS = {
    'kuaidaili': {
        'sess': sessions.get_default_session(),
        'xpath': '//table//tr',
        'url': 'https://www.kuaidaili.com/free/inha/{page_id}/'
    },
    'xiladaili': {
        'sess': sessions.get_default_session(),
        'xpath': '//table//tr',
        'url': 'http://www.xiladaili.com/gaoni/{page_id}/'
    }
}
