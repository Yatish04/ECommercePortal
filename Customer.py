import sqlite3
import json
from Transaction import *
from Order import *
import hashlib, os

class Customer(object):
    def __init__(self,email=None,password=None,id_=None):
        if id_ is None and email is not None and password is not None:
            self.status = self._login(email,password)
        else:
            self._email = email
            self._address = self.get_address(email)
            self.status = True

        if email is not None:
            self._email = email

        self._phoneno = 0
        
        self._name = ""
        self.db = sqlite3.connect('database.db')
	
    

    def _search(self,item_name):
        # Start of user code protected zone for search function body
        valid_dict={}
        cursor = self.db.cursor()
        cursor.execute(''' SELECT * FROM products WHERE name LIKE ?''',('%'+item_name+'%',))
        row=cursor.fetchone()
        all_dict={}
        count=0
        while  row is not None:
            valid_dict["Name"] = row[1]
            valid_dict["Quantity"] = row[2]
            valid_dict["Price"] = row[3]
            count+=1
            all_dict[count]=valid_dict
            row = cursor.fetchone()
        self.db.close()
        return all_dict
        # End of user code
        	
    def placingorder(self):

        js = self._transaction()
        if js:
            order = Order(self._email)
            products,totalprice = self.cart()
            for row in products:
                order.place_order(int(row[0]),row[1],self._address)
        
        return {"status":200,"totalprice":totalprice}

    
    @staticmethod
    def update(firstName, lastName, address1, address2, zipcode, city, state, country, phone, email):
        with sqlite3.connect('database.db') as con:
                try:
                    cur = con.cursor()
                    cur.execute('UPDATE users SET firstName = ?, lastName = ?, address1 = ?, address2 = ?, zipcode = ?, city = ?, state = ?, country = ?, phone = ? WHERE email = ?', (firstName, lastName, address1, address2, zipcode, city, state, country, phone, email))

                    con.commit()
                    msg = "Saved Successfully"
                except:
                    con.rollback()
                    msg = "Error occured"
        con.close()
        
        return msg

    def get_address(self,email):
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        self.email = email
        cur.execute('SELECT address1,address2,zipcode,city,state,country,phone FROM users WHERE email = ? ',(email,))
        rows = cur.fetchall()
        address = rows[0][0]+" "+rows[0][1]+" "+ rows[0][2]+" "+rows[0][3]+" "+rows[0][4]+" "+rows[0][5]+" "
        con.close()
        return address

    def _login(self,email, password):
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        self.email = email
        cur.execute('SELECT email, password FROM users')
        data = cur.fetchall()
        for row in data:
            if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
                return True
        return False

    @staticmethod
    def register(password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone):
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',(password, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone,))
                con.commit()

                msg = "Registered Successfully"
            except:
                con.rollback()
                msg = "Error occured"
        con.close()
        return msg

    def removeorder(self,productId):
        order = Order(self._email)
        order.removeorder(productId)
        return

    def get_order(self):
        ords = Order(self._email)
        products,price = ords.getorders()
        return {"status":200,"products":products,"price":price}
    
    def _transaction(self,type_=None,number=None):
        #call transaction here
        trans = Transaction(type_,number)
        status  = trans.get_status()
        return status



    def cart(self):
        totalPrice=0
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + self._email + "'")
            userId = cur.fetchone()[0]
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, kart WHERE products.productId = kart.productId AND kart.userId = " + str(userId))
            products = cur.fetchall()
        totalPrice = 0
        for row in products:
            totalPrice += row[2]
        return products,totalPrice

    def addcart(self,productId):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + self._email + "'")
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO kart (userId, productId) VALUES (?, ?)", (userId, productId))
                conn.commit()
                msg = "Added successfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        
    def removecart(self,productId):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + self._email + "'")
            userId = cur.fetchone()[0]
            try:
                cur.execute("DELETE FROM kart WHERE userId = " + str(userId) + " AND productId = " + str(productId))
                conn.commit()
                msg = "removed successfully"
            except:
                conn.rollback()
                msg = "error occured"
        conn.close()
