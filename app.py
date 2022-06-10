#All imports needed
from datetime import datetime
from flask_migrate import Migrate
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import MySQLdb.cursors

#initializing application
app = Flask(__name__)
#Removed the orignal credentials after deployment on heroku
#This is just the format for credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://<mysql user here >:<mysql password here>@<mysql db host here>:<port no here>/<db name here>'
#MySQL DB name
app.config['MYSQL_DB'] = 'db name here'
#MySQL Host name
app.config['MYSQL_HOST'] = 'host name here'
#MySQL username
app.config['MYSQL_USER'] = 'user name here'
#MySQL Password
app.config['MYSQL_PASSWORD'] = 'password here'
mysql = MySQL(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Can use this if needed

# if __name__ == "__main__":
#     app.run(host=os.getenv('IP', '0.0.0.0'),
#             port=int(os.getenv('PORT', 4444)))

#Transaction management table class, contains all the columns of transaction
class Transaction_info(db.Model):
    cust_id = db.Column(db.Integer, unique=False, nullable=False)
    amt_withdrawn = db.Column(db.Integer,unique=False, nullable=False)
    withdraw_time = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    receiver_id = db.Column(db.Integer,unique=False, nullable=False)
    transaction_id = db.Column(db.Integer,primary_key = True, unique=True, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


#Home route, first page to load on url
@app.route("/")
def home():
    return render_template("finances-master/index.html")


#Page to view all the customers data present in the database
@app.route("/view-all-customers",methods=['GET','POST'])
def viewCustomers():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # executing query
    cursor.execute("select * from customers_info")
    # fetching all records from database
    data = cursor.fetchall()
    cursor.close()

    return render_template("finances-master/customers.html", data=data)

#logic for transactions between selected users
@app.route("/transfer-money",methods=['GET','POST'])
def transfer():
    #when post request is sent
    if request.method == 'POST':
        '''Add entry to the database'''
        #gets ids of sender and receiver and the amount
        cust_id = request.form.get('sender')
        receiver_id = request.form.get('receiver')
        amt_withdrawn = request.form.get('amount')
        cust_id = int(cust_id)
        receiver_id = int(receiver_id)
        amt_withdrawn = int(amt_withdrawn)
        #records and commits the transacttion into the database
        entry = Transaction_info(cust_id=cust_id, receiver_id=receiver_id, amt_withdrawn=amt_withdrawn, withdraw_time=datetime.utcnow())
        db.session.add(entry)
        db.session.commit()
        conn = mysql.connection
        cursor = conn.cursor()
        #updates the balance for the sender and receiver
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
        #values are commited in customer table
        conn.commit()
        cursor.close()
        return render_template("finances-master/redirect.html")

    return render_template("finances-master/transfer.html")

#Redirect back to customers table to confirm the transaction yourself
@app.route("/redirect-to-customers")
def redirect():
    return render_template("finances-master/redirect.html")

#Not the best code but a try with flask which is not so common on web development
#Just a skeleton structure for any other improvements
