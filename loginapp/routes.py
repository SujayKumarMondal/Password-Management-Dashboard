import os
from os import urandom
import random
import sqlite3
import string
from PIL import Image
from flask import jsonify, render_template, flash, redirect, url_for, request
from loginapp import app, db, bcrypt, mail
from loginapp.forms import RegistrationForm, LoginForm, AddPassword, RequestResetForm, ResetPasswordForm, UserAccountUpdate, UpdatePassword
from loginapp.models import User, PasswordManager
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

def init_db():
    conn = sqlite3.connect('ext.db')
    cursor = conn.cursor()
    # Create the credentials table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            web_url TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the server starts
init_db()


@app.route('/generate_password', methods=['GET', 'POST'])
@login_required
def generate_password():
    if request.method == 'POST':
        # Get the form input
        length = int(request.form.get('length', 12))
        include_special = 'special' in request.form
        include_numbers = 'numbers' in request.form

        # Generate the password based on user input
        password = generate_random_password(length, include_special, include_numbers)
        return render_template('generate_password.html', password=password)

    return render_template('generate_password.html', password=None)

def generate_random_password(length, include_special, include_numbers):
    # Character sets for password generation
    characters = string.ascii_letters  # Letters (lower and uppercase)

    if include_numbers:
        characters += string.digits  # Add digits

    if include_special:
        characters += string.punctuation  # Add special characters

    # Generate a random password with the given length
    password = ''.join(random.choice(characters) for _ in range(length))

    return password


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    page_title = 'Register'
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Account Created. Now you can login.", 'success')
        send_registration_email(user.email)
        return redirect(url_for('home'))
    return render_template('register.html', title=page_title, form=form)

def send_registration_email(receiver_email):
    msg = Message('Welcome to Our App', sender=os.environ.get('MAIL_DEFAULT_SENDER'), recipients=[receiver_email])
    msg.body = 'Thank you for registering with us!'
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    page_title = 'Login'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('manager'))
        else:
            flash('Email or password does not match.', 'danger')
    return render_template('login.html', title=page_title, form=form)

@app.route('/manager')
@login_required
def manager():
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('manager.html', title='Manager', image_file=image_file)

@app.route('/manager/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddPassword()
    if form.validate_on_submit():
        name = db.session.query(User).filter_by(id=current_user.id).first()
        field = PasswordManager(webaddress=form.webaddress.data, username=form.username.data, email=form.email.data, password=form.password.data, owner=name)
        db.session.add(field)
        db.session.commit()
        return redirect(url_for('display'))
    return render_template('add.html', title='Add Password', form=form)

@app.route('/manager/display', methods=['GET', 'POST'])
@login_required
def display():
    fields = db.session.query(PasswordManager).filter_by(owner_id=current_user.id).all()
    return render_template('display.html', title='Display Passwords', elements=fields)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender=os.environ.get('MAIL_DEFAULT_SENDER'), recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, simply ignore this email.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('login'))
        else:
            flash('No account found with that email address.', 'danger')
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'danger')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been updated. Now you can login.", 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


# Endpoint to save the credentials
@app.route('/save_password', methods=['POST'])
def save_password():
    data = request.json
    web_url = data.get('web_url')
    password = data.get('password')
    
    if web_url and password:
        # Connect to the database
        conn = sqlite3.connect('ext.db')
        cursor = conn.cursor()
        
        # Insert the new credentials into the table
        cursor.execute("INSERT INTO credentials (web_url, password) VALUES (?, ?)", (web_url, password))
        conn.commit()
        conn.close()

        return jsonify({"message": "Password saved successfully!"}), 200
    
    return jsonify({"message": "Failed to save password, missing data."}), 400


def save_picture(form_picture):
    random_hex = urandom(8).hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (128, 128)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/manager/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UserAccountUpdate()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form)

@app.route('/delete/<int:sl>')
@login_required
def delete(sl):
    field = db.session.query(PasswordManager).filter_by(sl=sl).first()
    db.session.delete(field)
    db.session.commit()
    return redirect(url_for('display'))

@app.route('/update/<int:sl>', methods=['GET', 'POST'])
@login_required
def update(sl):
    form = UpdatePassword()
    values = db.session.query(PasswordManager).filter_by(sl=sl).first()
    if form.validate_on_submit():
        values.webaddress = form.webaddress.data
        values.username = form.username.data
        values.email = form.email.data
        values.password = form.password.data
        db.session.commit()
        return redirect(url_for('display'))
    elif request.method == 'GET':
        form.webaddress.data = values.webaddress
        form.username.data = values.username
        form.email.data = values.email
        form.password.data = values.password
    return render_template('update.html', title='Update', form=form)
