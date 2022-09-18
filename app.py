from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import ValidationError, InputRequired, Length, Email
from flask_bcrypt import Bcrypt
from uidgen import generateuid
from werkzeug.utils import secure_filename
from ipfs import Ipfs
import itertools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'MedBaseSecretKey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    cid = db.Column(db.String(), nullable=True)
    title = db.Column(db.String(), nullable=True)
    timestamp = db.Column(db.String(), nullable=True)

# db.create_all()

class RegistrationForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Name"})
    email = EmailField(validators=[InputRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError("That email is already registered! Try a different one.")

class LoginForm(FlaskForm):
    email = EmailField(validators=[InputRequired(), Email()], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    if current_user.cid is None:
        cid = []
        timestamp = []
        title = []
    else:
        cid = current_user.cid.split()
        title = current_user.title.split()
        timestamp = current_user.timestamp.split()
    uid = current_user.uid
    name = current_user.name
    email = current_user.email
    return render_template('dashboard.html', cids=cid, titles=title, timestamps=timestamp, zipped_data=zip(title, timestamp, cid), name=name, email=email, uid=uid)

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Incorrect Password! Please Try again")
        else:
            flash("This email is not registered. Try Signing Up!")


    return render_template('login-new.html', form=form)

@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password, uid=generateuid())
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register-new.html', form=form)

@app.route('/upload', methods=["GET", "POST"])
@login_required
def upload_file():

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(f"uploads/{filename}")
            metadata, timestamp = Ipfs.pinToIpfs(f"uploads/{filename}")

            if current_user.cid is None:
                user_cid = []
                user_timestamp = []
                user_file_title = []
            else:
                user_cid = current_user.cid.split()
                user_timestamp = current_user.timestamp.split()
                user_file_title = current_user.title.split()

            if metadata["IpfsHash"] in user_cid:
                print("This file already exists in your database.")
            else:
                user_cid.append(metadata["IpfsHash"])
                user_timestamp.append(timestamp)
                user_file_title.append(f"{filename}")
                current_user.cid = ' '.join(user_cid)
                current_user.timestamp = ' '.join(user_timestamp)
                current_user.title = ' '.join(user_file_title)
            db.session.commit()
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)