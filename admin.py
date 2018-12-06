import sqlite3
from datetime import datetime,timedelta


class Admin(object):
    def __init__(self,email=None,password=None):
        if(email is None and password is None):
            self.status = self._login(email,password)
        else:
            self.status=True
        return 


    def _login(self,email,password):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM admin WHERE email = ? AND password = ?",(email,password))
            categories = cur.fetchall()
        
        return len(categories)==0

    def add(self):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT categoryId, name FROM categories")
            categories = cur.fetchall()
        return categories

    def addItem(self,name, price, description, imagename, stock, categoryId):
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO products (name, price, description, image, stock, categoryId) VALUES (?, ?, ?, ?, ?, ?)''', (name, price, description, imagename, stock, categoryId,))
                conn.commit()
                cur.execute(''' SELECT productId FROM products WHERE name = ?''',(name,))
                prod_id = int(cur.fetchall()[0][0])
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        

        

        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''INSERT INTO add_item (adminid,productid) VALUES (?, ?)''', (1,prod_id,))
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        
        conn.close()
        print(msg)
        return msg

    def remove(self):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
            data = cur.fetchall()
        conn.close()
        return data

    def removeItem(self,productId):
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('DELETE FROM products WHERE productID = ' + productId)
                conn.commit()
                msg = "Deleted successsfully"
            except:
                conn.rollback()
                msg = "Error occured"
        conn.close()
        return msg

    def sold_items(self):
        with sqlite3.connect('database.db') as conn:
            date = datetime.now().strftime("%Y-%m-%d")
            oldtime = (datetime.now() -  timedelta(days=30)).strftime("%Y-%m-%d")
            total=0.0
            rows=[]
            try:
                cur = conn.cursor()

                cur.execute(''' SELECT * FROM orders WHERE date >= Datetime(?) AND date <= Datetime(?) ''',(oldtime,date,))
                rows = cur.fetchall()
                for i in rows:
                    cur.execute(''' SELECT price FROM products WHERE productId = ?''',(i[1],))
                    total+=cur.fetchall()[0][0]
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        return {"items":len(rows),"total":total}