from modules.hh_stats_class import HHStatistics
from modules.hh_area_class import HHArea


def show_main_menu():
    m_menu = """
************************************
**       Анализ вакансий HH       **
************************************
** 1. Изменить запрос вакансий    **
** 2. Задать регион               **
** 3. Запросить данные с HH       **
** 4. Вывести статистику          **
** 0. Выход                       **
************************************
    """
    print(m_menu)


if '__main__' == __name__:
    m_obj = HHStatistics()
    m_area = HHArea()
    m_area.initialize()
    while True:
        show_main_menu()
        m_choice = input('>> Ваш выбор: ')
        if '1' == m_choice:
            m_str = input('  Задайте строку запроса к HeadHunter: ')
            if len(m_str) < 1:
                print('  !!! ОШИБКА !!! > пустая строка не допускается.')
            else:
                m_obj.set_search_str(m_str)
            pass
        elif '2' == m_choice:
            m_area.reset()
            m_id, m_name = m_area.get_area()
            if m_id is not None:
                m_obj.set_area(m_id, m_name)
        elif '3' == m_choice:
            if len(m_obj.get_search_str()) < 1:
                print('  !!! ОШИБКА !!! > не задана строка поиска вакансий.')
            else:
                print('  Начали обмен данными с HeadHunters')
                m_obj.load_data()
                print('  Обмен данными завершён. Можете посмотреть статистику.')
        elif '4' == m_choice:
            print(m_obj.get_statistics())
        elif '0' == m_choice:
            break
