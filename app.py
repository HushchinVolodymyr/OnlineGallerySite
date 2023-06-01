from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import secrets
import os
import random

app = Flask(__name__)
app.app_context().push()

app.config['UPLOAD_FOLDER'] = 'static', 'images', 'pictures'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


secret_key = secrets.token_hex(32)
app.secret_key = secret_key

user_logging = False
user_login = ""
user_admin = False


def pictures_on_landing_page():
    picture_count = Picture.query.count()
    ids = []

    while len(ids) < 5:
        id = random.randint(1, picture_count)
        if id not in ids:
            ids.append(id)

    return ids

def authors_on_landing_page():
    author_count = Authors.query.count()
    ids = []

    while len(ids) < 3:
        id = random.randint(1, author_count)
        if id not in ids:
            ids.append(id)

    return ids


def get_picture_by_id(id):
    picture = Picture.query.filter_by(id=id).first()
    return picture


def get_author_by_id(id):
    author = Authors.query.filter_by(id=id).first()
    return author

def get_picture_by_name(name):
    picture = Picture.query.filter_by(picture_name = name).first()
    return picture


def get_author_by_name(name):
    author = Authors.query.filter_by(author_name = name).first()
    return author


def get_user_by_id(id):
    user = Users.query.filter_by(id=id).first()
    return user


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_picture_by_id(id):
    picture = Picture.query.get(id)
    if picture:
        db.session.delete(picture)
        db.session.commit()
        return True
    return False


def delete_author_by_id(id):
    author = Authors.query.get(id)
    if author:
        db.session.delete(author)
        db.session.commit()
        return True
    return False


def delete_user_by_id(id):
    user = Users.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False


def is_user_logged_in():
    return 'user_login' in session

def get_user_id(username):
    if is_user_logged_in():
        user = Users.query.filter_by(user_login=username).first()

        if user is None:
            return "User not found"
        
        user_id = user.id
        return str(user_id)

def get_picture_id(picture_name):
    picture = Picture.query.filter_by(picture_name=picture_name).first()

    if picture is None:
        return "Picture not found"
        
    picture_id = picture.id
    return picture_id

def get_author_id(author_name):
    
    author = Authors.query.filter_by(author_name=author_name).first()

    if author is None:
        return "Author not found"
        
    author_id = author.id
    return author_id

class Picture(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    picture_name = db.Column(db.String(200), nullable = False)
    picture_author = db.Column(db.String(200),nullable = False)
    picture_url = db.Column(db.Text, nullable = False)
    picture_description = db.Column(db.Text, nullable = False)

    def __repr__(self):
        return '<Picture %r>' % self.id


class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_login = db.Column(db.String(200), nullable = False)
    password = db.Column(db.Text, nullable = False)
    user_admin = db.Column(db.Boolean, default = False, nullable = False)

    def __repr__(self):
        return '<Users %r>' % self.id


class Authors(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    author_name = db.Column(db.String(200), nullable = False)
    author_url = db.Column(db.Text, nullable = False)
    author_description = db.Column(db.Text, nullable = False)

    def __repr__(self):
        return '<Authors %r>' % self.id


@app.route("/", methods=['POST', 'GET'])
@app.route("/home", methods=['POST', 'GET'])
def index():
    if is_user_logged_in():
        user_login = session['user_login']
        if 'user_admin' in session and session['user_admin'] == True:
            user_admin = "Додати картину"
        else:
            user_admin = ""

    else:
        user_login = "Увійти"
        user_admin = ""

    if request.method == 'POST':
        search_name = request.form['query']
        picture = get_picture_by_name(search_name)

        if picture is not None:
            picture_name = picture.picture_name
            picture_author = picture.picture_author
            picture_path = picture.picture_url
            picture_dicrpt = picture.picture_description
            picture_full_name = f"{picture_author} \"{picture_name}\""
        else:
            author = get_author_by_name(search_name)

            if author is not None:
                author_name = author.author_name
                author_path = author.author_url
                author_discrpt = author.author_description
            else:
                return redirect('/')

            return render_template("author.html", author_name=author_name, author_path=author_path, author_discrpt=author_discrpt, username = user_login)

                

        return render_template("picture.html", picture_full_name=picture_full_name, picture_path=picture_path, picture_discrpt=picture_dicrpt, username = user_login)

    else:
        ids = pictures_on_landing_page()
        auth_id = authors_on_landing_page()

        main_picture_url = get_picture_by_id(ids[0]).picture_url
        first_picture_url = get_picture_by_id(ids[1]).picture_url
        second_picture_url = get_picture_by_id(ids[2]).picture_url
        third_picture_url = get_picture_by_id(ids[3]).picture_url
        fourth_picture_url = get_picture_by_id(ids[4]).picture_url

        first_author_url = get_author_by_id(auth_id[0]).author_url
        second_author_url = get_author_by_id(auth_id[1]).author_url
        third_author_url = get_author_by_id(auth_id[2]).author_url

        main_picture_name = f"{get_picture_by_id(ids[0]).picture_author} \"{get_picture_by_id(ids[0]).picture_name}\""
        first_picture_name = f"{get_picture_by_id(ids[1]).picture_author} \"{get_picture_by_id(ids[1]).picture_name}\""
        second_picture_name = f"{get_picture_by_id(ids[2]).picture_author} \"{get_picture_by_id(ids[2]).picture_name}\""
        third_picture_name = f"{get_picture_by_id(ids[3]).picture_author} \"{get_picture_by_id(ids[3]).picture_name}\""
        fourth_picture_name = f"{get_picture_by_id(ids[4]).picture_author} \"{get_picture_by_id(ids[4]).picture_name}\""

        first_author_name = get_author_by_id(auth_id[0]).author_name
        second_author_name = get_author_by_id(auth_id[1]).author_name
        third_author_name = get_author_by_id(auth_id[2]).author_name
        return render_template("index.html", third_author_id=auth_id[2],second_author_id=auth_id[1],first_author_id=auth_id[0],third_author_url=third_author_url, second_author_url=second_author_url, first_author_url=first_author_url, third_author_name=third_author_name, second_author_name=second_author_name, first_author_name = first_author_name, main_picture_id=ids[0], first_picture_id=ids[1], second_picture_id=ids[2], third_picture_id=ids[3], fourth_picture_id=ids[4] ,username=user_login, main_picture_url=main_picture_url, first_picture_url=first_picture_url, second_picture_url=second_picture_url, third_picture_url=third_picture_url, fourth_picture_url=fourth_picture_url, main_picture_name=main_picture_name, first_picture_name=first_picture_name, second_picture_name=second_picture_name, third_picture_name=third_picture_name, fourth_picture_name=fourth_picture_name, admin = user_admin)


@app.route("/pictures/<image_id>")
def picture(image_id): 
    id = int(image_id) 
    picture = get_picture_by_id(id)

    if is_user_logged_in():
        user_login = session['user_login']
    else:
        user_login = "Увійти"

    if picture is not None:
        picture_name = picture.picture_name
        picture_author = picture.picture_author
        picture_path = picture.picture_url
        picture_dicrpt = picture.picture_description
        picture_full_name = f"{picture_author} \"{picture_name}\""
    else:
        print("Not found this stroke")

    return render_template("picture.html", picture_full_name=picture_full_name, picture_path=picture_path, picture_discrpt=picture_dicrpt, username = user_login)


@app.route("/author/<image_id>")
def author(image_id): 
    id = int(image_id) 
    author = get_author_by_id(id)

    if is_user_logged_in():
        user_login = session['user_login']
    else:
        user_login = "Увійти"

    if author is not None:
        author_name = author.author_name
        author_path = author.author_url
        author_discrpt = author.author_description
    else:
        print("Not found this stroke")

    return render_template("author.html", author_name=author_name, author_path=author_path, author_discrpt=author_discrpt, username = user_login)



@app.route("/addpicture", methods=['POST', 'GET'])
def add_picture():
    if is_user_logged_in():
        user_login = session['user_login']
    else:
        user_login = "Увійти"

    if request.method == "POST":
        picture_name = request.form['picture-name']
        author_name =  request.form['author']
        picture_description = request.form['description']
        img = request.files['file-input']
        filename = img.filename
        present_in_table = False
       
        pictures = Picture.query.all()
        pictures_names = []

        for picture in  pictures:
            pictures_names.append(picture.picture_name)

        if picture_name in pictures_names:
            present_in_table = True
        
        if present_in_table == False:
            try:
                if request.method == "POST":
                    if allowed_file(filename):
                        img = request.files["file-input"]
                        filename = img.filename
                        img.save(f"static/images/pictures/{filename}")
                        file_path = "../static/images/pictures/" + str(filename)

                picture = Picture(picture_name=picture_name, picture_author=author_name, picture_description=picture_description, picture_url = file_path)
                db.session.add(picture)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                print(f"При додавання картини сталась помилка! Помилка: {str(e)}")
                return "При додавання картини сталась помилка!"
        else:
            return render_template("addpicture.html", username = user_login)

    else:
        return render_template("addpicture.html", username = user_login)


@app.route("/preview", methods=['POST'])
def preview_image():
    if request.method == "POST":
        img = request.files['file']
        if img and allowed_file(img.filename):
            file_data = img.read()
            return file_data


@app.route("/addauthor", methods=['POST', 'GET'])
def addauthor():
    if is_user_logged_in():
        user_login = session['user_login']
    else:
        user_login = "Увійти"

    if request.method == "POST":
        author_name =  request.form['author']
        author_description = request.form['description']
        img = request.files['file-input']
        filename = img.filename
        present_in_table = True
        
        authors = Authors.query.all()
        authors_names = []

        for author in  authors:
            authors_names.append(author.author_name)

        if author_name in authors_names:
            present_in_table = True
        
        if present_in_table == False:
            try:
                if request.method == "POST":
                    if allowed_file(filename):
                        img = request.files["file-input"]
                        filename = img.filename
                        img.save(f"static/images/authors/{filename}")
                        file_path = "../static/images/authors/" + str(filename)
                
                author = Authors(author_name = author_name, author_description = author_description, author_url = file_path)
                db.session.add(author)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                print(f"При додавання автора сталась помилка! Помилка: {str(e)}")
                return "При додавання автора сталась помилка!"
        else:
            return render_template("addauthor.html", username = user_login)

    else:
        return render_template("addauthor.html", username = user_login)


@app.route("/login", methods=['POST', 'GET'])
def login():
    if is_user_logged_in():
        user_login = session['user_login']
    else:
        user_login = "Увійти"

    if request.method == "POST":
        user_login = request.form['login']
        present_in_table = False

        users = Users.query.all()
        users_logins = []

        for user in users:
            users_logins.append(user.user_login)

        if request.form['login'] in users_logins:
            present_in_table = True

        if present_in_table:
            user = Users.query.filter_by(user_login=request.form['login']).first()
            if user:
                user_password = user.password

                if check_password_hash(user_password, request.form['password']):
                    session['user_logging'] = True
                    session['user_login'] = str(user_login)
                    user_id = get_user_id(request.form['login'])
                    user = get_user_by_id(user_id)
                    if user.user_admin == True:
                        session['user_admin'] = True
                    return redirect('/')
                else:
                    return "Incorrect data!!!!"
            else:
                return "User not found!!!"
        else:
            return "User not found!!!"

    else:
         return render_template("login.html", username = user_login)


@app.route("/register", methods=['POST', 'GET'])
def register():
    if is_user_logged_in():
        user_login = session['user_login']
    else:
        user_login = "Увійти"

    if request.method == "POST":
        user_login = request.form['login']
        user_password = request.form['password']
        user_password_confirm = request.form['password-confirm']
        user_admin = False
        present_in_table = False

        users = Users.query.all()
        users_logins = []

        for user in  users:
            users_logins.append(user.user_login)

        if user_login in users_logins:
            present_in_table = True
        
        if present_in_table == False:
            if len(user_password) >= 8:
                if user_password == user_password_confirm:
                    if 'myCheckbox' in request.form:
                        try:
                            hash = generate_password_hash(user_password)
                            user = Users(user_login = user_login, password = hash, user_admin = user_admin)
                            db.session.add(user)
                            db.session.commit()
                            return redirect('/login')
                        except Exception as e:
                            print(f"User reg error {str(e)}")
                            return "User reg error"

        return render_template("register.html", username = user_login)
    else:
        return render_template("register.html", username = user_login)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)

