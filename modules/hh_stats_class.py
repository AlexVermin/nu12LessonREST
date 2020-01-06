import requests
import time
import json
import os


API_URL = 'https://api.hh.ru'
VACANCIES = f'{API_URL}/vacancies'
SAVE_PLACE = './saved_reqs'


class HHStatistics:

    def __init__(self):
        self._str_search = ''
        self._area = 0
        self._area_name = ''
        self._stats = ''

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

    def set_area(self, p_id, p_name):
        self._area = p_id
        self._area_name = p_name
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
        m_result['avg_salary'] = round(m_result['avg_salary'] / m_result['count'], 2)
        skill_list = list(m_result['skills'].items())
        skill_list.sort(key=lambda z: z[1], reverse=True)
        m_result['skills'] = skill_list
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


if '__main__' == __name__:
    obj = HHStatistics()
    obj.set_search_str('python developer')
    obj.set_area(2, 'Санкт-Питербург')
    obj.load_data()
    print(obj.get_statistics())
