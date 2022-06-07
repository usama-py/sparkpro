import json
import os
from datetime import datetime
from urllib import response
from flask_migrate import Migrate
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors
#port = int(os.getenv('PORT'))
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/bank'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://lzrkvgzfsidrjc:d4f285e33b206cb4da033cea6a1aa0a203f448d7bc0b98b41fdc389366de14a3@ec2-44-196-223-128.compute-1.amazonaws.com:5432/dcma9cm3p2i2io'
#app.config['MYSQL_DB'] = 'bank'
#app.config['MYSQL_HOST'] = 'localhost'
#ySQL username
#app.config['MYSQL_USER'] = 'root'
#MySQL password here in my case password is null so i left empty
#app.config['MYSQL_PASSWORD'] = ''
mysql = MySQL(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class Transaction_info(db.Model):
    cust_id = db.Column(db.Integer, unique=False, nullable=False)
    amt_withdrawn = db.Column(db.Integer,unique=False, nullable=False)
    withdraw_time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    receiver_id = db.Column(db.Integer,unique=False, nullable=False)
    transaction_id = db.Column(db.Integer,primary_key = True, unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username



@app.route("/")
def home():
    return render_template("finances-master/index.html")


@app.route("/view-all-customers",methods=['GET','POST'])
def viewCustomers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from customers_info")
    # fetching all records from database
    data = cursor.fetchall()
    cursor.close()



    return render_template("finances-master/customers.html", data=data)

@app.route("/transfer-money",methods=['GET','POST'])
def transfer():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from customers_info")
    # fetching all records from database
    data = cursor.fetchall()
    if request.method == 'POST':
        '''Add entry to the database'''
        cust_id = request.form.get('sender')
        receiver_id = request.form.get('receiver')
        amt_withdrawn = request.form.get('amount')
        cust_id = int(cust_id)
        receiver_id = int(receiver_id)
        amt_withdrawn = int(amt_withdrawn)
        entry = Transaction_info(cust_id=cust_id, receiver_id=receiver_id, amt_withdrawn=amt_withdrawn, withdraw_time=datetime.utcnow())
        db.session.add(entry)
        db.session.commit()
        conn = mysql.connection
        cursor = conn.cursor()

        cursor.execute('select balance from customers_info where cust_id = %s', (cust_id,))
        amt_withdrawn = int(amt_withdrawn)
        balance1 = cursor.fetchone()
        x=balance1[0]
        x=x - amt_withdrawn
        cursor.execute('select balance from customers_info where cust_id = %s', (receiver_id,))
        balance2 = cursor.fetchone()
        y = balance2[0]
        y=y + amt_withdrawn
        stmt1 = "update customers_info set balance = %s where cust_id = %s"
        cursor.execute(stmt1, (x, cust_id,))
        conn.commit()
        stmt2 = "update customers_info set balance = %s where cust_id = %s"
        cursor.execute(stmt2, (y, receiver_id,))


        conn.commit()
        cursor.close()
        return render_template("finances-master/customers.html",data=data)

    return render_template("finances-master/transfer.html")


app.run(debug=True)
