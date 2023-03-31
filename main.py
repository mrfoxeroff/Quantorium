from flask import Flask, render_template, abort
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import Api
from werkzeug.utils import redirect
from data import db_session
from data.users import User
from forms.user import LoginForm
from requests import *
from data.functions import get_information, get_status

app = Flask(__name__)
app.config['SECRET_KEY'] = 'quantorium280323'
app.config['JSON_AS_ASCII'] = False
api = Api(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    information = get_information()
    status_names = ['Выключен', "Работает", "Ожидание", "Ошибка"]
    av_speeds = []
    status_dict = [0, 0, 0, 0]
    for i in range(1, 7):
        av_speeds.append(information[i]['load_h'][1])
        status_dict[information[i]['status']] += 1
    count_h = information[6]['count_h']
    count_d = information[6]['count_d']
    bad_count = information[2]['count_d']
    try:
        bad_percent = round(bad_count / count_h, 2) * 100
    except ZeroDivisionError:
        bad_percent = 0
    wait_dict = {0: "Не ожидает", 1: "Ожидает заготовки", 2: "Линия переполнена"}
    return render_template('index.html', title="Статистика линии", info=information,
                           asd=sum(av_speeds) / 6, statuses=status_dict,
                           status_names=status_names,
                           cah=count_h, cad=count_d, bc=bad_count, bcp=bad_percent,
                           wt=wait_dict)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            return redirect("/")
        return render_template('login.html',
                               message="Неверный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/monitor', methods=['GET'])
def online_monitor():
    information = get_information()
    return render_template('online.html', title='Онлайн монитор', info=information)


@app.route('/info/cell=<int:id>', methods=['GET'])
def cell_information(id):
    information = get_information()[id]
    for i in range(4):
        information['load_h'][i] = round(information['load_h'][i], 2)
        information['load_d'][i] = round(information['load_d'][i], 2)
    statuses = get_status(id)
    status_names = ['Выключен', "Работает", "Ожидание", "Ошибка"]
    return render_template('info.html', title='Информация о ячейке', info=information,
                           statuses=statuses, status_names=status_names)


def main():
    db_session.global_init('db/users_database.db')
    app.run()


if __name__ == '__main__':
    main()
