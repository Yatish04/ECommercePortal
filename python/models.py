import sqlite3 as sql



def retrieveUsers(username,password):
	con = sql.connect("db1")
	cur = con.cursor()
	cur.execute("SELECT * FROM ships WHERE sellerid = (SELECT sellerid FROM seller WHERE sellerid = '"+username+"' AND passwords ='"+password+"')")
	users = cur.fetchall()
	con.close()
        return users


def verify(username,password):
	con = sql.connect("db1")
	cur = con.cursor()
	cur.execute("SELECT * FROM ships WHERE sellerid = (SELECT sellerid FROM seller WHERE sellerid = '"+username+"' AND passwords ='"+password+"')")
	users = cur.fetchall()
	con.close()
        return users

