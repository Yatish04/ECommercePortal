
from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import sqlite3
import models as dbHandler
import json
app = Flask(__name__)



@app.route('/', methods=['POST', 'GET'])
def orders():    		
	return render_template('index.html')




@app.route('/orders',methods=['POST','GET'])
def ordersview():
        print session
	if request.method=='POST':
    		username = request.form['username']
   		password = request.form['password']

        users = dbHandler.retrieveUsers(username,password)
	if len(users)!=0:
		return render_template('orders.html', users=users)
	else:
		return render_template('register.html')
   	

 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=7000)
