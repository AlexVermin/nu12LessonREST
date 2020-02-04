from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from modules.hh_stats_class import HHStatistics
from modules.hh_area_class import HHArea

web = Flask(__name__)

SECURITY_DATA = './data/token.data'
TOP_SECRET_KEY = ''
TITLES = {
    'getstats': 'Создание запроса',
    'results': 'Отображение статистики',
    'about': 'Контактная информация',
    'login': 'Проверка доступа',
    'main': 'Главная страница'
}


def check_admin():
    if 'is_admin' not in session:
        session['is_admin'] = '0'
    return session['is_admin']


@web.route('/')
def show_default_page():
    return render_template('index.html', is_admin=check_admin())


@web.route('/about/')
def show_about_page():
    return render_template('about.html', page='about', page_title=TITLES['about'], is_admin=check_admin())


"""
@web.route('/<page>')
def main_handler(page):
    m_title = ''
    m_template = 'index.html'
    if page is not None and page in TITLES.keys():
        m_title = TITLES[page]
        m_template = f'{page}.html'
    return render_template(m_template, page=page, page_title=m_title, is_admin=check_admin())
"""


@web.route('/results/', defaults={'show_obj': None})
@web.route('/results/<show_obj>')
def show_results_page(show_obj):
    m_template = 'results.html'
    m_stats = HHStatistics()
    if show_obj is not None:
        m_template = 'show_stats.html'
        m_obj_list = m_stats[show_obj]
        # print(m_obj_list)
    else:
        m_obj_list = m_stats.get_list()
        # print(m_obj_list)
    return render_template(
        m_template,
        page='results',
        page_title=TITLES['results'],
        is_admin=check_admin(),
        m_table=m_obj_list
    )


@web.route('/login/', methods=['GET', 'POST'])
def do_login():
    m_template = 'login.html'
    m_page = 'login'
    m_fail = '0'
    if 'POST' == request.method:
        m_pass = request.form['text']
        if m_pass == TOP_SECRET_KEY:
            session['is_admin'] = '1'
            return redirect(url_for('show_default_page'))
        else:
            m_fail = '1'
    return render_template(
        m_template,
        page=m_page,
        page_title=TITLES[m_page],
        is_admin=check_admin(),
        login_failed=m_fail
    )


@web.route('/logout/')
def do_logout():
    session['is_admin'] = '0'
    return redirect(url_for('show_default_page'))


@web.route('/getstats/', methods=['GET'])
def show_form_page():
    m_list = HHArea()
    return render_template(
        'request.html',
        page='getstats',
        page_title=TITLES['getstats'],
        areas=m_list.get_list(),
        is_admin=check_admin()
    )


@web.route('/getarea/', defaults={'area': None})
@web.route('/getarea/<area>', methods=['GET'])
def get_area_list(area):
    # print('param: ', area)
    m_list = HHArea()
    return jsonify(m_list.get_list(area))


@web.route('/getstats/', methods=['POST'])
def load_data():
    m_obj = HHStatistics()
    m_obj.set_search_str(request.form['text'])
    m_obj.set_area(int(request.form['area']))
    print(f'txt => {request.form["text"]}')
    print(f'rgn => {request.form["area"]}')
    m_obj.load_data()
    return redirect(url_for('show_results_page'))


if __name__ == "__main__":
    m_key = None
    try:
        with open(SECURITY_DATA, 'rt', encoding='utf-8') as f:
            m_key = f.readline().strip()
            TOP_SECRET_KEY = f.readline().strip()
    except FileNotFoundError:
        print(f'''
Для работы необходим файл "{SECURITY_DATA}", содержащий секретный ключ для работы Flask с сессиями
и паролем администратора сайта.
''')

    if len(m_key) > 0 and len(TOP_SECRET_KEY) > 0:
        web.secret_key = m_key
        web.run(debug=True)
    else:
        print('Не заданы настройки. Работа прекращена.')
