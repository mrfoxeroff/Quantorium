from datetime import datetime
from requests import get

current_time = datetime.timestamp((datetime.now()))
begin_of_the_day = current_time - (current_time % (3600 * 24))


def get_status():
    information_dict = {1: {'id': 1,
                            'name': "Выкладка фишек",
                            'count_an_hour': 0,
                            'count_a_day': 0,
                            'load_an_hour': 0,
                            'load_a_day': 0},
                        2: {'id': 2,
                            'name': "Сортировка",
                            'count_an_hour': 0,
                            'count_a_day': 0,
                            'load_an_hour': 0,
                            'load_a_day': 0
                            },
                        3: {'id': 3,
                            'name': 'Маркировка',
                            'count_an_hour': 0,
                            'count_a_day': 0,
                            'load_an_hour': 0,
                            'load_a_day': 0
                            },
                        4: {'id': 4,
                            'name': 'Выкладка оснований',
                            'count_an_hour': 0,
                            'count_a_day': 0,
                            'load_an_hour': 0,
                            'load_a_day': 0
                            },
                        5: {'id': 5,
                            'name': 'Раскладка',
                            'count_an_hour': 0,
                            'count_a_day': 0,
                            'load_an_hour': 0,
                            'load_a_day': 0
                            },
                        6: {'id': 6,
                            'name': 'Упаковка',
                            'count_an_hour': 0,
                            'count_a_day': 0,
                            'load_an_hour': 0,
                            'load_a_day': 0
                            }}
    for i in range(1, 7):
        status = get(f"http://roboprom.kvantorium33.ru/api/current?cell={i}").json()
        count_hour_time = get(f"http://roboprom.kvantorium33.ru/api/history?cell={i}&param=count"
                              f"&from={current_time - 3600}&to={current_time}").json()
        count_day_time = get(f"http://roboprom.kvantorium33.ru/api/history?cell={i}&param=count"
                             f"&from{begin_of_the_day}&to={begin_of_the_day + 3600 * 24}").json()
        status_day_time = get(f'http://roboprom.kvantorium33.ru/api/history?cell={i}'
                              f'&param=status'
                              f'&from={begin_of_the_day}'
                              f'&to={begin_of_the_day + 3600 * 24}').json()
        status_hour_time = get(f'http://roboprom.kvantorium33.ru/api/history?cell={i}'
                               f'&param=status'
                               f'&from={current_time - 3600}'
                               f'&to={current_time}').json()
        count_day = 0
        count_hour = 0
        load_day = 0
        load_hour = 0
        for elem in status['data']:
            for k in elem['params']:
                if k['param'] == 'status':
                    information_dict[i]['status'] = k['value']
                elif k['param'] == 'wait':
                    information_dict[i]['status'] = k['value']
            fl = False
            all_time = 0
            prev_ts = 0
            prev_status = -1
            for k in status_hour_time['data']:
                if k['value'] in (1, 2):
                    if not fl:
                        fl = True
                        prev_ts = k['ts']
                if k['value'] in (0, 4) and prev_status in (1, 2):
                    all_time += max(k['ts'] - prev_ts, 0)
                    fl = False
                prev_status = k['value']
            try:
                if status_hour_time['data'][-1]['value'] in (1, 2):
                    all_time += max(current_time - status_hour_time['data'][-1]['ts'], 0)
            except IndexError:
                pass
            information_dict[i]['load_an_hour'] = round(all_time, 2)
            fl = False
            all_time = 0
            prev_ts = 0
            prev_status = -1
            for k in status_day_time['data']:
                if k['value'] in (1, 2):
                    if not fl:
                        fl = True
                        prev_ts = k['ts']
                if k['value'] in (0, 4) and prev_status in (1, 2):
                    all_time += max(k['ts'] - prev_ts, 0)
                    fl = False
                prev_status = k['value']
            try:
                if status_day_time['data'][-1]['value'] in (1, 2):
                    all_time += max(current_time - status_day_time['data'][-1]['ts'], 0)
            except IndexError:
                pass
            information_dict[i]['load_a_day'] = round(all_time, 2)
        for elem in count_day_time['data']:
            information_dict[i]['count_a_day'] = elem['value']
        for elem in count_hour_time['data']:
            information_dict[i]['count_an_hour'] = elem['value']
    return information_dict


def get_count():
    count_per_hour = 0
    count_per_day = 0
    bad_count = 0
    bad_count_percent = 0
    params = []
    for i in range(1, 7):
        current_cell_per_hour = get(f'http://roboprom.kvantorium33.ru/api/history?cell={i}&param=count'
                                    f'&from={current_time - 3600}&to={current_time}').json()
        current_cell_per_day = get(f'http://roboprom.kvantorium33.ru/api/history?cell={i}&param=count'
                                   f'&from={current_time - 3600 * 24}&to={current_time}').json()
        if i == 6:
            for j in current_cell_per_hour['data']:
                count_per_hour += j['value']
            for j in current_cell_per_hour['data']:
                count_per_day += j['value']
        if i == 2:
            for j in current_cell_per_day['data']:
                bad_count += j['value']
    params.append(count_per_hour)
    params.append(count_per_day)
    params.append(bad_count)
    try:
        params.append(bad_count / count_per_day)
    except ZeroDivisionError:
        params.append(0)
    return params


def average_speed():
    av_cells_speeds = []
    for i in range(1, 7):
        current_cell_per_hour = get(f'http://roboprom.kvantorium33.ru/api/history?cell={i}'
                                    f'&param=status'
                                    f'&from={current_time - 3600}'
                                    f'&to={current_time}').json()
        fl = False
        all_time = 0
        prev_ts = 0
        prev_status = -1
        for k in current_cell_per_hour['data']:
            if k['value'] in (1, 2):
                if not fl:
                    fl = True
                    prev_ts = k['ts']
            if k['value'] in (0, 4) and prev_status in (1, 2):
                all_time += k['ts'] - prev_ts
                fl = False
            prev_status = k['value']
        try:
            if current_cell_per_hour['data'][-1]['value'] in (1, 2):
                all_time += current_time - current_cell_per_hour['data'][-1]['ts']
        except IndexError:
            pass
        av_cells_speeds.append(100 * (all_time / 3600))
    return sum(av_cells_speeds) / len(av_cells_speeds)


def volume_per_day():
    api = get(f"http://roboprom.kvantorium33.ru/api/history?cell=6"
              f"&from={begin_of_the_day}"
              f"&to={begin_of_the_day + 3600 * 24}"
              f"&param=count").json()
    hours = []
    for i in range(0, 24):
        count = 0
        for j in api['data']:
            if j['ts'] in range(int(begin_of_the_day + 3600 * i), int(begin_of_the_day + 3600 * (i + 1) + 1)):
                count = j['value']
        hours.append(count)
    return hours
