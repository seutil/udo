from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.secret_key = 'секретный_ключ'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def get_id(self):
        return str(self.id)

# Функция для проверки валидности email
def is_valid_email(email):
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        return False

# Инициализация приложения и базы данных
def create_app():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        # Проверка валидности email
        if not is_valid_email(email):
            flash('Invalid email address', 'error')
            return redirect(url_for('index'))

        # Проверка совпадения пароля и подтверждения пароля
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('index'))

        # Проверка существования пользователя с таким email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User with this email already exists', 'error')
            return redirect(url_for('index'))

        # Регистрация нового пользователя
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful', 'success')
        return redirect(url_for('success'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)
            flash('Login successful', 'success')
            return redirect(url_for('success'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

@app.route('/success')
@login_required
def success():
    return render_template('success.html')

if __name__ == '__main__':
    with app.app_context():
        create_app()
    app.run(debug=True)