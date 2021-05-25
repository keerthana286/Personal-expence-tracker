from flask import Flask,flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash
import MySQLdb.cursors
import re
from datetime import datetime
from helper import login_required
from sendemail import sendgridmail
app = Flask(__name__)
app.secret_key = 'a'
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'C5hcD0YorY'
app.config['MYSQL_PASSWORD'] = 'TdpZ0SD2Rm'
app.config['MYSQL_DB'] = 'C5hcD0YorY'
mysql = MySQL(app)

@app.route('/', methods = ['GET'])
def index():
    return render_template("index.html")

@app.route('/credit', methods = ['GET','POST'])
def credit():
    if request.method == 'POST':
        userid = session["user_id"]
        amount = float(request.form['amount'])
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT balance FROM users where id = {}".format(userid))
        rows = cursor.fetchall()
        balance = rows[0][0]
        if(amount<0):
            flash("Can't Credit, enter correct amount")
            return redirect("/transaction")
        balance += float(amount)
        type_of_transaction = "C"
        today=datetime.now()
        cursor.execute("INSERT INTO transactions(userid, reason, type, amount,timestamp) VALUES (% s,% s,% s,% s,% s)",(userid,request.form['about'],type_of_transaction,request.form['amount'],today,))
        mysql.connection.commit()
        cursor.execute("UPDATE users SET balance =% s WHERE id =% s",(balance,userid,))
        mysql.connection.commit()
        flash("CREDITED current balance is {}".format(balance))
        return redirect("/transaction")
          
@app.route('/debit', methods = ['GET','POST'])
def debit():
    if request.method == 'POST':
        userid = session["user_id"]
        cursor = mysql.connection.cursor()
        amount = float(request.form['amount'])
        cursor.execute("SELECT balance FROM users where id = {}".format(userid))
        rows = cursor.fetchall()
        balance = rows[0][0]
        if(balance<amount):
            flash("Can't Debit, your balance is {}".format(balance))
            return redirect("/transaction")
        balance -= amount
        type_of_transaction = "D"
        today=datetime.now()
        cursor.execute("INSERT INTO transactions(userid, reason, type, amount,timestamp) VALUES (% s,% s,% s,% s,% s)",(userid,request.form['about'],type_of_transaction,request.form['amount'],today,))
        mysql.connection.commit()
        cursor.execute("UPDATE users SET balance =% s WHERE id =% s",(balance,userid,))
        mysql.connection.commit()
        flash("DEBITED current balance is {}".format(balance))
        return redirect("/transaction")

@app.route('/login', methods=['GET', 'POST'])
def login():
    global userid 
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        account = cursor.fetchone()  
        if account:
            pd=account[3]
            if check_password_hash(pd,password):
                session['loggedin'] = True
                session['user_id'] = account[0]
                userid =  account[0]
                session['username'] = account[1]
                return redirect("/")
        else:
            flash("User does not exists")
    return render_template("login.html")

@app.route('/register', methods =['GET', 'POST'])
def register():
    if request.method == 'POST' :
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'  
        username = request.form['username']
        email = request.form['inputEmail']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))  
        account = cursor.fetchall()
        if account:
            flash("User already exists")
        elif confirmPassword!=password:
            flash("Passwords does not match")
        elif not (re.match(regex,email)):
            flash("Invalid email address !")
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash("Name must contain only characters and numbers!")
        else:
            password=generate_password_hash(password)
            TEXT = "Hello "+username + ",\n\n"+ """Thanks for registering at PERSONAL EXPENSE TRACKER """ 
            TEXT+="\n\n\n\n{}".format("""Expense tracker helps you to keep an accurate record of your money inflow and outflow. When you track your spending, you know where your money goes and you can ensure that your money is used wisely. Tracking your expenditures also allows you to understand why you're in debt and how you got there. This will then help you design a befitting strategy of getting out of debt.""")
            message  = 'Subject: {}\n\n{}'.format("Personal Expense Tracker", TEXT)
            x=sendgridmail(email,TEXT)
            if x==1:
                flash("You have successfully registered on PERSONAL EXPENSE TRACKER ")
                cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s,% s)', (username,email,password,'0'))
                mysql.connection.commit()
            else:
                flash("Oops..! Your registration failed")
            return redirect("/")
    return render_template("register.html")

@app.route('/transaction',methods = ['GET','POST'])
@login_required
def transaction():
    return render_template("transaction.html")
    


@app.route('/statement', methods = ['GET'])
@login_required
def statement():
    userid = session["user_id"]
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM transactions where userid = {}".format(userid))
    rows=cursor.fetchall()
    cursor.execute("SELECT balance FROM users where id = {}".format(userid))
    row = cursor.fetchall()
    balance=row[0][0]   
    return render_template("statement.html", records = rows, balance=balance)
    
@app.route("/logout") 
@login_required   
def logout():
    session.clear()
    return redirect("/")
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug = True,port = 8080)
