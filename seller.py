import sqlite3 as sql




class Seller:

    @staticmethod
    def retrieveUsers(username,password):
        con = sql.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM ships WHERE sellerid = (SELECT sellerid FROM seller WHERE sellername = '"+username+"' AND passwords ='"+password+"')")
        users = cur.fetchall()
        con.close()
        return users

    @staticmethod
    def verify(username,password):
        con = sql.connect("database.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM seller WHERE sellername = ? AND passwords = ?",(username,password,))
        users = cur.fetchall()
        con.close()
        return users

    @staticmethod
    def update(name, price, description, imagename, stock, categoryId):
        with sql.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute('''UPDATE products SET price = ?, description = ?, image = ?, stock = stock + ?, categoryId = ? WHERE name = ? ''', (price, description, imagename, stock, categoryId,name,))
                
                conn.commit()
                msg="added successfully"
            except:
                msg="error occured"
                conn.rollback()
        conn.close()
        print(msg)
        return msg
    
    @staticmethod
    def updatetable(name,sellerid):
        with sql.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute(''' SELECT productId from products WHERE name = ? ''',(name,))
                id_ = cur.fetchall()[0][0]
                cur.execute('''INSERT INTO update_item (ProductID,SellerID) VALUES (?,?)''',(id_,sellerid))
                
                conn.commit()
            except:
                print("Someerror")
        return
