from flask import Flask, render_template, request, abort, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy

from flask_pymongo import PyMongo
from flask import jsonify

import os
import sys

DEBUG = True
SECRET_KEY = 'yekterces'
SQLALCHEMY_DATABASE_URI = 'sqlite:///db/sql.db'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['MONGO_DBNAME'] = 'local'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/local'

mongo = PyMongo(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    HomeFolder = db.Column(db.String)
    ShellType = db.Column(db.String)
    privilege = db.Column(db.String)
@login_manager.user_loader
def user_loader(user_id):
    user = User.query.filter_by(id=user_id)
    if user.count() == 1:
        return user.one()
    return None

@app.before_first_request
def init_request():
    db.create_all()

@app.route('/options', methods=['GET', 'POST'])
@login_required
def options():
    if request.method == 'GET':
        users = User.query.all()
        return render_template('options.html',test=users)
       
    elif request.method == 'POST':
        id = request.form['txtid']
        user = User.query.filter_by(id=id)

        db.session.delete(user.one())
        db.session.commit()
        flash('You have deleted the username')
        return redirect(url_for('logout'))

    else:
        abort(405)

#def secret():
   
    #return render_template('index.html')
        

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['txtUsername']
        password = request.form['txtPassword']
        HomeFolder = request.form['HomeFolder']
        ShellType = request.form['ShellType']
        privilege = request.form['privilege']
        user = User.query.filter_by(username=username).filter_by(password=password)
        if user.count() == 0:
            user = User(username=username, password=password, HomeFolder=HomeFolder, ShellType=ShellType, privilege=privilege)
            db.session.add(user)
            db.session.commit()
            test = mongo.db.user
            test.insert({'Username': username,'pwd':password,'homefolder':HomeFolder,'shell':ShellType})


            flash('You have registered the username {0}. Please login'.format(username))
            return redirect(url_for('login'))
        else:
            flash('The username {0} is already in use.  Please try a new username.'.format(username))
            return redirect(url_for('register'))
    else:
        abort(405)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', next=request.args.get('next'))
    elif request.method == 'POST':
        username = request.form['txtUsername']
        password = request.form['txtPassword']

        user = mongo.db.testLogin
        for usr in user.find():
            userName = usr['_id']
            pwd = usr['pwd']
            role = usr['role']
            if(userName == username and pwd == password):
                if(role == 'farmer'):
                    flash('Welcome back farmer {0}'.format(username))
                    try:
                        next = request.form['next']
                        return redirect(next)
                    except:
                        return redirect(url_for('index'))
                else:
                    flash('Welcome back investor {0}'.format(username))
                    try:
                        next = request.form['next']
                        return redirect(next)
                    except:
                        return redirect(url_for('index'))
        else:
            flash('Invalid login')
            return redirect(url_for('login'))
    else:
        return abort(405)

@app.route('/modify', methods=['GET', 'POST'])
def modify():
    if request.method == 'GET':
        return render_template('modify.html')
    elif request.method == 'POST':
        username = request.form['xUsername']
        password = request.form['xPassword']
        HomeFolder = request.form['xHomeFolder']
        ShellType = request.form['xShellType']
        privilege = request.form['xprivilege']
        id=request.form['txtid']
        user = User.query.filter_by(username=username).filter_by(password=password)
        if user.count() == 1:
            user = User(username=username, password=password, HomeFolder=HomeFolder, ShellType=ShellType, privilege=privilege)
            db.session.delete(user.one())
            db.session.add(user)
            db.session.commit()
            flash('You have registered the username {0}. Please login'.format(username))
            return redirect(url_for('modify'))
        else:
            flash('The username {0} is already in use.  Please try a new username.'.format(username))
            return redirect(url_for('modify'))
    else:
        abort(405)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('IP', '127.0.0.1')
    app.run(port=port, host=host)
