import requests
import time
import json
import os
from modules.hh_area_class import HHArea
import sqlite3

API_URL = 'https://api.hh.ru'
VACANCIES = f'{API_URL}/vacancies'
SAVE_PLACE = './saved_reqs' if '__main__' == __name__ else './modules/saved_reqs'
DB_PATH = '../data/site_data.db' if '__main__' == __name__ else 'data/site_data.db'


class HHStatistics:

    def __init__(self):
        self._str_search = ''
        self._area = 0
        self._area_name = ''
        self._stats = ''
        self._db = None
        self._crs = None
        if len(DB_PATH) > 0:
            self._db = sqlite3.connect(DB_PATH, check_same_thread=True)
            self._crs = self._db.cursor()

    def get_search_str(self):
        return self._str_search

    def set_search_str(self, p_str):
        self._str_search = p_str
        self._stats = ''

    def clear_search_str(self):
        self._str_search = ''
        self._stats = ''

    def get_area_id(self):
        return self._area

    def get_area_name(self):
        return self._area_name

    def set_area(self, p_id, p_name=None):
        self._area = p_id
        m_name = p_name
        if m_name is None:
            m_area = HHArea()
            m_name = m_area.load_area_by_id(p_id)
        self._area_name = m_name
        self._stats = ''

    def clear_areas(self):
        self._area = 0
        self._area_name = ''
        self._stats = ''

    def load_data(self):
        req_count = 0
        skill_count = 0
        if len(self._str_search) > 0:
            m_params = {'text': self._str_search, 'per_page': 20}
            m_result = {'text': self._str_search}
            if self._area > 0:
                m_params['area'] = self._area
                m_result['area'] = self._area
                m_result['area_name'] = self._area_name
            m_result['skills'] = {}
            m_result['count'] = 0
            m_result['avg_salary'] = 0
            m_result['min_salary'] = 0
            m_result['max_salary'] = 0
            m_params['page'] = 0
            while True:
                if 0 == req_count % 100:
                    time.sleep(5)
                    # print('sleep_5_01')
                m_js_data = requests.get(VACANCIES, params=m_params).json()
                print(f'    обрабатывается страница {m_params["page"]+1} из {m_js_data["pages"]}')
                req_count += 1
                if 'items' not in m_js_data.keys():
                    return -2  # ошибка в запросе
                else:
                    for item in m_js_data['items']:
                        m_info = requests.get(f'{VACANCIES}/{item["id"]}').json()
                        req_count += 1
                        if 0 == req_count % 100:
                            time.sleep(5)
                            # print('sleep_5_02')
                        if 'salary' in m_info.keys():
                            if m_info['salary'] is not None:
                                q = 0
                                s = 0
                                if 'from' in m_info['salary'].keys() and m_info['salary']['from'] is not None:
                                    s += m_info['salary']['from']
                                    if 0 == m_result['min_salary']:
                                        m_result['min_salary'] = m_info['salary']['from']
                                    else:
                                        if m_info['salary']['from'] < m_result['min_salary']:
                                            m_result['min_salary'] = m_info['salary']['from']
                                    q += 1
                                if 'to' in m_info['salary'].keys() and m_info['salary']['to'] is not None:
                                    s += m_info['salary']['to']
                                    if 0 == m_result['max_salary']:
                                        m_result['max_salary'] = m_info['salary']['to']
                                    else:
                                        if m_info['salary']['to'] > m_result['max_salary']:
                                            m_result['max_salary'] = m_info['salary']['to']
                                    q += 1
                                if \
                                        'to' in m_info['salary'].keys() \
                                        and 'from' in m_info['salary'].keys() \
                                        and m_info['salary']['to'] is None \
                                        and m_info['salary']['from'] is not None:
                                    if 0 == m_result['max_salary']:
                                        m_result['max_salary'] = m_info['salary']['from']
                                    else:
                                        if m_info['salary']['from'] > m_result['max_salary']:
                                            m_result['max_salary'] = m_info['salary']['from']
                                if \
                                        'to' in m_info['salary'].keys() \
                                        and 'from' in m_info['salary'].keys() \
                                        and m_info['salary']['to'] is not None \
                                        and m_info['salary']['from'] is None:
                                    if 0 == m_result['min_salary']:
                                        m_result['min_salary'] = m_info['salary']['to']
                                    else:
                                        if m_info['salary']['to'] < m_result['min_salary']:
                                            m_result['min_salary'] = m_info['salary']['to']
                                m_result['avg_salary'] += s / q
                        if 'key_skills' in m_info.keys():
                            for skill in m_info['key_skills']:
                                if skill['name'] in m_result['skills'].keys():
                                    m_result['skills'][skill['name']] += 1
                                else:
                                    m_result['skills'][skill['name']] = 1
                                skill_count += 1
                        m_result['count'] += 1
                    m_params['page'] += 1
                    if m_params['page'] == m_js_data['pages']:
                        break  # дошли до конца списка - выйти из цикла поиска
                # break
        else:
            return -1  # не задана строка поиска
        # всё ок, значит надо сохранить статистику в файл
        m_result['avg_salary'] = 0 if 0 == m_result['count'] else round(m_result['avg_salary'] / m_result['count'], 2)
        skill_list = list(m_result['skills'].items())
        skill_list.sort(key=lambda z: z[1], reverse=True)
        m_result['skills'] = skill_list
        if self._db is not None:
            self.save_obj(m_result)
        else:
            if not os.path.exists(SAVE_PLACE):
                os.makedirs(SAVE_PLACE)
            with open(f'{SAVE_PLACE}/{time.strftime("%Y%m%d_%H%M%S")}', 'w') as f:
                json.dump(m_result, f)
        self._stats = f'.... Запрос: "{m_result["text"]}"\n'
        if 'area' in m_result.keys():
            self._stats += f'.... Регион: "{m_result["area_name"]}"\n'
        self._stats += f'.... По запросу найдено вакансий: {m_result["count"]-1}\n'
        self._stats += f'.... Средний уровень заработной платы: {m_result["avg_salary"]}\n'
        self._stats += f'.... Минимальное предложение по заработной плате: {m_result["min_salary"]}\n'
        self._stats += f'.... Максимальное предложение по заработной плате: {m_result["max_salary"]}\n'
        self._stats += f'.... Список требований к вакансии:\n'
        for item in m_result['skills']:
            self._stats += f'....   - {item[0]}: {item[1]} ({round(item[1] / skill_count * 100, 2)}%)\n'
        return 0  # всё ок

    def get_statistics(self):
        return self._stats

    def _db_exists(self, p_key):
        m_res = False
        if self._db is not None:
            self._crs.execute('select id from main_data where req_time = ?', (p_key,))
            m_check = self._crs.fetchall()
            m_res = len(m_check) > 0
        return m_res

    def get_list(self):
        m_res = {}
        if os.path.exists(f'{SAVE_PLACE}'):
            m_files = [z for z in os.listdir(f'{SAVE_PLACE}') if os.path.isfile(f'{SAVE_PLACE}/{z}')]
            m_files.sort()
            for item in m_files:
                with open(f'{SAVE_PLACE}/{item}', 'r') as f:
                    js = json.load(f)
                if not self._db_exists(item):
                    m_res[item] = {
                        'query': js['text'],
                        'place': js['area_name'],
                        'time': time.strftime('%d.%m.%Y %H:%M:%S', time.strptime(item, '%Y%m%d_%H%M%S'))
                    }
        if self._db is not None:
            for item in self._crs.execute(
                '''
                select m.id, m.req_text, m.req_time, a.name
                from main_data m inner join areas a on a.id = m.area_id
                order by m.req_time
                '''
                                          ):
                m_res[item[2]] = {
                    'query': item[1],
                    'place': item[3],
                    'time': time.strftime('%d.%m.%Y %H:%M:%S', time.strptime(item[2], '%Y%m%d_%H%M%S')),
                    'obj': f'item_{item[0]}'
                }
        return m_res

    def __getitem__(self, item):
        m_list = self.get_list()
        m_js = {}
        # print(f'{SAVE_PLACE}/{item}')
        if item in m_list.keys():
            # print(f'{item} is in the list')
            if self._db is not None:
                m_obj = self._crs.execute(
                        '''
                        select
                            m.req_text, m.req_time, m.vacancy_count,
                            m.avg_salary, m.min_salary, m.max_salary,
                            a.name, m.id
                        from main_data m
                            inner join areas a on a.id = m.area_id
                        where m.req_time = ?
                        ''',
                        (item, )
                    ).fetchone()
                if m_obj is not None:
                    m_js = {
                        'text': m_obj[0],
                        'obj': m_obj[1],
                        'vacancy_count': m_obj[2],
                        'avg_salary': m_obj[3],
                        'min_salary': m_obj[4],
                        'max_salary': m_obj[5],
                        'area_name': m_obj[6],
                        'in_db': '1'
                    }
                    m_skills = self._crs.execute(
                            '''
                            select
                                s.name, u.freq_count
                            from user_skills u
                                inner join skills s on s.id = u.skill_id
                            where u.data_id = ?
                            order by u.freq_count desc
                            ''',
                            (m_obj[7],)
                        ).fetchall()
                    if len(m_skills) > 0:
                        m_js['skills'] = []
                        wgt = 0
                        for skill in m_skills:
                            m_js['skills'].append([skill[0], skill[1]])
                            wgt += skill[1]
                        m_js['total_wgt'] = wgt
            if m_js == {}:
                with open(f'{SAVE_PLACE}/{item}') as f:
                    m_js = json.load(f)
                if 'skills' in m_js.keys():
                    total_wgt = 0
                    for x in m_js['skills']:
                        total_wgt += x[1]
                    m_js['total_wgt'] = total_wgt
                m_js['vacancy_count'] = m_js['count']
                del m_js['count']
                m_js['in_db'] = '1' if self._db_exists(item) else '0'
                m_js['obj'] = item
            return m_js
        else:
            return None

    def save_obj(self, p_obj):
        m_time = time.strftime("%Y%m%d_%H%M%S")
        p_obj['vacancy_count'] = p_obj['count']
        p_obj['in_db'] = '0'
        return self.do_save(m_time, p_obj)

    def save_file(self, p_time):
        m_obj = self.__getitem__(p_time)
        return self.do_save(p_time, m_obj)

    def do_save(self, p_time, p_obj):
        # print(p_obj)
        # return False
        m_obj = p_obj
        if m_obj is not None:
            if '0' == m_obj['in_db']:
                m_data = (
                    m_obj['text'],
                    m_obj['area'],
                    p_time,
                    m_obj['vacancy_count'],
                    m_obj['min_salary'],
                    m_obj['max_salary'],
                    m_obj['avg_salary']
                )
                self._crs.execute(
                    '''insert into main_data (
                        req_text, area_id, req_time, vacancy_count, min_salary, max_salary, avg_salary
                    ) values (?, ?, ?, ?, ?, ?, ?)''',
                    m_data
                )
                self._db.commit()
                db_obj = self._crs.execute('select id from main_data where req_time = ?', (p_time,)).fetchone()
                if db_obj is None:
                    return False
                else:
                    s_data = []
                    for s in m_obj['skills']:
                        db_skill = self._crs.execute('select id from skills where name = ?', (s[0],)).fetchone()
                        if db_skill is not None:
                            s_data.append(
                                (db_obj[0], db_skill[0], s[1])
                            )
                        else:
                            self._crs.execute('insert into skills (name) values (?)', (s[0],))
                            self._db.commit()
                            db_skill = self._crs.execute('select id from skills where name = ?', (s[0],)).fetchone()
                            s_data.append(
                                (db_obj[0], db_skill[0], s[1])
                            )
                    self._crs.executemany(
                        'insert into user_skills (data_id, skill_id, freq_count) values (?, ?, ?)',
                        s_data
                    )
                    self._db.commit()
                    return True
        return False


if '__main__' == __name__:
    obj = HHStatistics()
    obj.save_file('20200204_235915')
    # print(s)
