from flask import Flask, render_template, url_for, flash, redirect, request,jsonify
from forms import *
import forms
import pandas as pd
import uuid
import log_in_check as check
import pymysql
from QueryEngine import QueryEngine
from flask_mail import Mail, Message
from random import randint


qe = QueryEngine()
qe.setup_default()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a26ade032e7040309ba635818774a38b'


mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "uhdatabase2019@gmail.com"
app.config['MAIL_PASSWORD'] = "coscspring2019"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



transaction_id = randint(10, 999999)


@app.route("/")
@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/menu")
def menu():
    return render_template('menu.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user.data
        password = form.password.data
        if check.login_check(username, password) == True:
            return redirect(url_for('manager_view'))
        else:
            flash('Invalid Account, Check Your Username and Password', 'danger')
    return render_template('login.html',form=form)


@app.route("/manager_view", methods=['GET', 'POST'])
def manager_view():
    return render_template('manager_view.html')


@app.route("/survey", methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if form.validate_on_submit():

        global transaction_id
        sex = form.sex.data
        ethnicity = form.ethnicity.data
        zipcode = form.zipcode.data
        age = form.age.data
        first_name = form.first_name.data

        qe.connect()
        query_string = f"INSERT INTO Survey VALUES({transaction_id},'{sex}','{ethnicity}',{age},{zipcode},'{first_name}');"
        qe.do_query(query_string)
        qe.commit()
        qe.disconnect()

        return redirect(url_for('menu'))

    return render_template('survey.html',form=form)


@app.route("/cart", methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        response = request.get_json(force=True)  # parse as JSON
        keys = list(response.keys())

        #check history transaction 
        global transaction_id
        transaction_id_exist_check = check.transaction_check(transaction_id)
        while(transaction_id_exist_check == False):
            transaction_id = randint(10, 999999)
            transaction_id_exist_check = check.transaction_check(transaction_id)

        transaction_id +=1

        for i in range(len(keys)):
            food_id = keys[i]
            food_name = response[food_id][0]
            quantity = response[food_id][1]
            qe.connect()
            query_string = f"INSERT INTO Transaction VALUES({transaction_id},{food_id},'{food_name}',{quantity});"
            qe.do_query(query_string)
            qe.commit()
            qe.disconnect()
    else:
        return redirect(url_for('survey'))


if __name__ == '__main__':
    app.run(debug =True)





