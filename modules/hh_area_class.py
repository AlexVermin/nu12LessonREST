import requests


API_URL = 'https://api.hh.ru/areas/'


class HHArea:

    def __init__(self):
        self._obj = []
        self._current = None
        self._name = None

    def get_list(self, item=None):
        m_addr = API_URL if item is None else f'{API_URL}{item}'
        m_data = requests.get(m_addr).json()
        del self._obj[:]
        m_list = m_data if item is None else m_data['areas']
        # print(m_list)
        for item in m_list:
            self._obj.append(
                {
                    'id': item['id'],
                    'name': item['name'],
                    'has_child': 1 if len(item['areas']) > 0 else 0
                }
            )
        self._current = None
        self._name = None
        return self._obj

    def reset(self):
        self._current = None
        self._name = None

    @staticmethod
    def _area_choice(obj):
        m_selection = None
        m_name = None
        selected_has_child = True
        obj_list = obj
        obj_list.sort(key=lambda z: int(z['id']))
        while True:
            print('  Выбор региона:')
            for item in obj_list:
                has_child = '***' if len(item['areas']) > 0 else '...'
                if m_selection == int(item['id']):
                    is_selected = '+>'
                    selected_has_child = len(item['areas']) > 0
                else:
                    is_selected = '  '
                print(f'    {is_selected}{item["id"]:>8} => {{{has_child}}} {item["name"]}')
            print('  '+'='*30)
            if m_selection is not None:
                print('    p => Задать выбранный регион')
                if selected_has_child:
                    print('    s => Показать вложенные регионы')
            print('    q => Выйти без заданного региона')
            m_choice = input('  Ваш выбор: ')
            if 'q' == m_choice:
                return None, None
            elif m_selection is not None and 'p' == m_choice:
                return m_selection, m_name
            elif m_selection is not None and 's' == m_choice:
                for item in obj:
                    if m_selection == int(item['id']):
                        m_selection, m_name = HHArea._area_choice(item['areas'])
                        break
                return m_selection, m_name
            else:
                is_ok = False
                for item in obj:
                    if m_choice == item['id']:
                        m_selection = int(m_choice)
                        m_name = item['name']
                        is_ok = True
                        break
                if not is_ok:
                    print('    Неверный ввод.')

    def _select_area(self):
        m_obj = self._area_choice(self._obj)
        if 'q' == m_obj:
            self._current = None
        else:
            self._current = m_obj

    def get_area(self):
        self._select_area()
        return self._current

    def get_region(self):
        return self._current

    def _get_obj(self):
        # m_res = []
        # if parent is not None:
        #     for item in self._obj:
        #         print(item['id'], ' <=> ', parent)
        #         if int(item['id']) == parent:
        #             for area in item['areas']:
        #                 m_res.append({'id': area['id'], 'name': area['name']})
        # else:
        #     for item in self._obj:
        #         m_res.append({'id': item['id'], 'name': item['name']})
        return self._obj

    @staticmethod
    def load_area_by_id(p_id=None):
        m_res = None
        if p_id is not None:
            m_obj = requests.get(f'{API_URL}{p_id}').json()
            if 'name' in m_obj:
                m_res = m_obj['name']
        return m_res


if '__main__' == __name__:
    m_area = HHArea()
    print(m_area.load_area_by_id(1002))
    # print(HHArea.load_area_by_id(4))
