import sqlite3
class Order(object):
    def __init__(self,email):
        self._cstid = self._getId(email)
        self._email=email
        

        
    # Start of user code -> properties/constructors for Order class

    # End of user code

    def _getId(self,email):
        db = sqlite3.connect('database.db')
        cursor = db.cursor()
        cursor.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cursor.fetchone()[0]
        return userId



    # End of user code
    def getorders(self):
        totalPrice=0
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            # cur.execute("SELECT userId FROM users WHERE email = '" + self._email + "'")
            # userId = cur.fetchone()[0]
            cur.execute("SELECT products.productId, products.name, products.price, products.image FROM products, orders WHERE products.productId = orders.productId AND orders.custid = " + str(self._cstid))
            products = cur.fetchall()
        totalPrice = 0
        for row in products:
            totalPrice += row[2]
        return products,totalPrice

    def removeorder(self,productId):
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM orders WHERE productId = ? AND  custid = ? ", (int(productId),int(self._cstid)))
            cur.execute("UPDATE products SET stock = stock + ? WHERE productId = ?",(1,int(productId),))
            conn.commit()
            
        return

    def place_order(self,productId,productname,address):
        conn = sqlite3.connect('database.db') 
        cursor = conn.cursor()
        userId = self._cstid
        
        cursor.execute(''' SELECT * FROM kart WHERE userId = ?''',(int(userId),)) # select all products
        cursor.execute('''SELECT stock FROM products WHERE productId = ?''',(int(productId),))
        tupstock=cursor.fetchall()
        stock = int(tupstock[0][0])
        if stock>0:
            cursor.execute(''' INSERT INTO orders(custid,productId) VALUES (?,?) ''',(int(userId),int(productId),)) # insert item id and customer id and item id
            cursor.execute('''UPDATE products SET stock = stock - ? WHERE productId = ?''',(1,int(productId),))
            cursor.execute('''DELETE FROM kart WHERE productId = ? AND userId = ?''',(int(productId),int(userId),))
            cursor.execute(''' INSERT INTO ships(customerid,productid,shipperid,sellerid,address) VALUES (?,?,?,?,?) ''',(int(userId),productname,"bluedart",1,address,)) 
            conn.commit()
            conn.close()
            return
        else:
            raise Exception("No more stocks left")
