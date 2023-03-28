from flask import Flask, render_template, abort
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_restful import Api
from werkzeug.utils import redirect
from data import db_session
from data.users import User
from forms.user import LoginForm, RegisterForm
from requests import *

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
@app.route('/index')
def index():
    results = get("http://roboprom.kvantorium33.ru/api/current").json()
    statuses = get_status(results)
    return render_template('index.html', title="Статистика линии")


def get_status(res):
    statuses = []
    status_ids = {0: 'Выключена', 1: "Работает", 2: 'Ожидание', 3: 'Ошибка'}
    for i in res['data']:
        cell_number = i['cell']
        cell_status = status_ids[i['params'][0]['value']]
        statuses.append((cell_number, cell_status))
    return statuses


@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Данная почта уже зарегистрированна")
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message='Данное имя пользоватея уже существует')
        if not form.agreement.data:
            return render_template('registration.html', title="Регистрация",
                                   form=form,
                                   message='Вы не приняли пользовательское соглашение')
        user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неверный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


def main():
    db_session.global_init('db/users_database.db')
    app.run()


if __name__ == '__main__':
    main()
