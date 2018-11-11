import sqlite3


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