import os
import requests

from flask import Flask, session, flash
from flask import render_template, request, redirect
from flask import url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from models import *
from waitress import serve

app = Flask(__name__)

# Check for environment variable
#if not os.getenv("DATABASE_URL"):
#raise RuntimeError("DATABASE_URL is not set")

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://eegfjegitfwjpd:10dc44b25f3a970cc60e798dddcf6e0d60719873542f35468bef133c5ce1965b@ec2-54-246-89-234.eu-west-1.compute.amazonaws.com:5432/d6o4kqf8gea8g3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#engine = create_engine(os.getenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))
#set DATABASE_URL=postgres://eegfjegitfwjpd:10dc44b25f3a970cc60e798dddcf6e0d60719873542f35468bef133c5ce1965b@ec2-54-246-89-234.eu-west-1.compute.amazonaws.com:5432/d6o4kqf8gea8g3

#API info
#APIkey: 1GapN0pUcioQ8rN9EnLcVg
#APIsecret: 4aG2mrZiYhYQASBkqQtZkDlAepY3c3yKDIXPT9B0
#import requests
#res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})
#print(res.json())

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '#6ghu439f0$'
#Session(app)

class RegisterForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired(),EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

loggedin = False
data = []
user = []

@app.route("/")
def index():
    global user
    user = []
    book = books.query.filter_by(ratings = 4.5).all()
    if loggedin==True:
        fname = users.query.filter_by(id=session["user_id"]).first().fname
        user.append(fname)
        lname = users.query.filter_by(id=session["user_id"]).first().lname
        user.append(lname)
    else:
        user = None
    return render_template('index.html', loggedin=loggedin, book=book, user=user)    
    
@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    global loggedin
    if form.validate_on_submit():
        try:
            user = users.query.filter_by(username=form.username.data).first_or_404()
            if (form.password.data==user.password):
                loggedin = True
                session["user_id"] = user.id
                session.modified = True
                if form.remember_me.data==True:
                    session.permanent = True
                return redirect(url_for('index'))
            else: 
                return render_template('login.html', loggedin=loggedin, user=user, error='Incorrect Username/Password.')
        except:
            return render_template('login.html', form=form, user=user, loggedin=loggedin, error='Incorrect Username/Password.')  
    return render_template('login.html', title='Sign In', form=form, loggedin=loggedin)


@app.route("/register", methods=["GET","POST"])
def register():
    form = RegisterForm()
    global loggedin
    if form.validate_on_submit():
        try:
            user = users(fname=form.fname.data, lname=form.lname.data, username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            db.session.close()
            return redirect(url_for('login'))
        except:
            return render_template("register.html", title='Sign Up', form=form, user=user, error='Username/password already taken!', loggedin=loggedin)
    return render_template("register.html", title='Sign Up', form=form, loggedin=loggedin)

@app.route("/logout", methods=["GET","POST"])
def logout():
    global loggedin
    loggedin=False
    return redirect('/')

@app.route("/search", methods=["GET","POST"])
def search():
    global data
    if request.method == "POST":
        term = request.form.get("search").title()
        print(term)
    data = []
    book = books.query.filter(books.title.contains(term)).all()
    for b in book:
        data.append(b)
    print("...")
    author = books.query.filter(books.author.contains(term)).all()
    for a in author:
        data.append(a)
    print(data)
    db.session.close()
    return redirect(url_for('results'))

@app.route("/results")
def results():
    return render_template('books.html', loggedin=loggedin, user=user, data=data)

@app.route("/isbn/<string:isbn>", methods=['GET','POST'])
def book(isbn):
    book = books.query.filter_by(ISBN=isbn).first()
    if request.method == 'POST':
        review = request.form.get("review")
        username = users.query.filter_by(id=session["user_id"]).first().username
        myreview = reviews(username= username, review_id= book.id, review=review)
        db.session.add(myreview)
        db.session.commit()
        message = "Submitted succesfully"
    review = reviews.query.filter_by(review_id=book.id).all()
    db.session.close()
    return render_template("book.html", loggedin=loggedin, user=user, book=book, review=review)

if __name__=="__main__":
    #app.run()
    serve(app, host='0.0.0.0', port=8000)

