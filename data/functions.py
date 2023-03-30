import pprint
from datetime import datetime
from requests import get

current_time = datetime.timestamp((datetime.now()))
begin_of_the_day = current_time - (current_time % (3600 * 24) + 3600 * 3)


def get_information():
    information_dict = {1: {'id': 1,
                            'name': "Выкладка фишек",
                            'count_h': 0,
                            'count_d': 0,
                            'load_h': 0,
                            'load_d': 0,
                            },
                        2: {'id': 2,
                            'name': "Сортировка",
                            'count_h': 0,
                            'count_d': 0,
                            'load_h': 0,
                            'load_d': 0,
                            },
                        3: {'id': 3,
                            'name': 'Маркировка',
                            'count_h': 0,
                            'count_d': 0,
                            'load_h': 0,
                            'load_d': 0,
                            },
                        4: {'id': 4,
                            'name': 'Выкладка оснований',
                            'count_h': 0,
                            'count_d': 0,
                            'load_h': 0,
                            'load_d': 0,
                            },
                        5: {'id': 5,
                            'name': 'Раскладка',
                            'count_h': 0,
                            'count_d': 0,
                            'load_h': 0,
                            'load_d': 0,
                            },
                        6: {'id': 6,
                            'name': 'Упаковка',
                            'count_h': 0,
                            'count_d': 0,
                            'load_h': 0,
                            'load_d': 0,
                            }}
    current_api = get("http://roboprom.kvantorium33.ru/api/current").json()['data']
    for i in range(1, 7):
        information_dict[i]['count_h'] = current_api[i - 1]['count_h']
        information_dict[i]['count_d'] = current_api[i - 1]['count_d']
        information_dict[i]['load_h'] = [x * 100 for x in current_api[i - 1]['load_h']]
        information_dict[i]['load_d'] = [x * 100 for x in current_api[i - 1]['load_d']]
        information_dict[i]['status'] = current_api[i - 1]['status']
        information_dict[i]['wait'] = current_api[i - 1]['wait']
    return information_dict


def get_status(id):
    api = get(f'http://roboprom.kvantorium33.ru/api/history?cell={id}'
              f'&param=status'
              f'&from={begin_of_the_day}&to={current_time}').json()['data']
    statuses = [0, 0, 0, 0]
    for i in api:
        statuses[i['value']] += 1
    return statuses
