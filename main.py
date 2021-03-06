from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
from Customer import *
from admin import *
from seller import *
from pymongo import *

app = Flask(__name__)
app.secret_key = 'random string'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def getLoginDetails():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            loggedIn = False
            firstName = ''
            noOfItems = 0
        else:
            loggedIn = True
            cur.execute("SELECT userId, firstName FROM users WHERE email = '" + session['email'] + "'")
            userId, firstName = cur.fetchone()
            cur.execute("SELECT count(productId) FROM kart WHERE userId = " + str(userId))
            noOfItems = cur.fetchone()[0]
    conn.close()
    return (loggedIn, firstName, noOfItems)

@app.route("/")
def root():
    search = request.args.get('searchQuery')
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if search is None:
            cur.execute('SELECT productId, name, price, description, image, stock FROM products')
        
        else:
            cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE name LIKE ?',('%'+search+'%',))
        itemData = cur.fetchall()
        cur.execute('SELECT categoryId, name FROM categories')
        categoryData = cur.fetchall()
    itemData = parse(itemData)   
    return render_template('home.html', itemData=itemData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryData=categoryData)





@app.route("/admin")
def adminlogin():

    return render_template("adminlogin.html")

@app.route('/admin/login',methods= ["POST"])
def admin_login():
    data = request.get_json()
    admin = Admin(email=data["email"],password=data["password"])
    if admin.status:
        session["type"] = "admin"
        session["user"] = data["email"]
        
        return json.dumps({"status":200})
    else:
        raise InvalidUsage('Invalid Credentials', status_code=415)



@app.route("/add.html")
def admin():
    if "user" in session and session["type"] == "admin":
        admin = Admin()
        categories = admin.add()
        return render_template('add.html', categories=categories)
    else:
        raise InvalidUsage('Invalid Credentials', status_code=415)

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if request.method == "POST":
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        stock = int(request.form['stock'])
        categoryId = int(request.form['category'])

        #Uploading image procedure
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        imagename = filename

        if "user" in session and session["type"] == "admin":
            admin = Admin()
            msg = admin.addItem(name, price, description, imagename, stock, categoryId)
            return redirect(url_for('root'))

        else:
            raise InvalidUsage('Invalid Credentials', status_code=415)


@app.route("/remove")
def remove():
    if "user" in session and session["type"] == "admin":
        admin = Admin()
        data = admin.remove()
        
    
    return render_template('remove.html', data=data)


@app.route("/admin/sales")
def sales():
    admin = Admin()
    data = admin.sold_items()
    return "Total Number of Items sold are :"+"<b>"+str(data["items"])+"</b><br/><br/> Total Cost of Items sold are :"+"<b>"+str(data["total"])+" $ </b>"

@app.route("/review",methods=["POST"])
def review():
    data = request.get_json()
    # import pdb; pdb.set_trace()
    productid = data["productid"]
    email = session["email"]
    review = data["review"]
    user = email.split("@")
    username = user[0]
    client = MongoClient('localhost', 27017)
    db = client.lab
    cur = db.labs.find({"id":str(productid)})
    out = list(cur)
    if(len(out)==0):
        new_dict = {"id":str(productid),username:review}
        db.labs.insert_one(new_dict)
    else:
        dict_ = out[0]
        dict_[user[0]] = review
        db.labs.update_one({"id":str(productid)},{"$set":dict_},upsert=False)

    return json.dumps({"status":200})
    




@app.route("/removeItem")
def removeItem():
    productId = request.args.get('productId')
    if "user" in session and session["type"] == "admin":
        admin = Admin()
        data = admin.removeItem(productId)
    
    print(data)
    return redirect(url_for('root'))

@app.route("/displayCategory")
def displayCategory():
        loggedIn, firstName, noOfItems = getLoginDetails()
        categoryId = request.args.get("categoryId")
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT products.productId, products.name, products.price, products.image, categories.name FROM products, categories WHERE products.categoryId = categories.categoryId AND categories.categoryId = " + categoryId)
            data = cur.fetchall()
        conn.close()
        categoryName = data[0][4]
        data = parse(data)
        return render_template('displayCategory.html', data=data, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems, categoryName=categoryName)

@app.route("/account/profile")
def profileHome():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    return render_template("profileHome.html", loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/edit")
def editProfile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("editProfile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/account/profile/view")
def view_profile():
    if 'email' not in session:
        return redirect(url_for('root'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId, email, firstName, lastName, address1, address2, zipcode, city, state, country, phone FROM users WHERE email = '" + session['email'] + "'")
        profileData = cur.fetchone()
    conn.close()
    return render_template("profile.html", profileData=profileData, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)





@app.route("/account/profile/changePassword", methods=["GET", "POST"])
def changePassword():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
        
    if request.method == "POST":
        oldPassword = request.form['oldpassword']
        oldPassword = hashlib.md5(oldPassword.encode()).hexdigest()
        newPassword = request.form['newpassword']
        newPassword = hashlib.md5(newPassword.encode()).hexdigest()
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId, password FROM users WHERE email = '" + session['email'] + "'")
            userId, password = cur.fetchone()
            if (password == oldPassword):
                try:
                    cur.execute("UPDATE users SET password = ? WHERE userId = ?", (newPassword, userId))
                    conn.commit()
                    msg="Changed successfully"
                except:
                    conn.rollback()
                    msg = "Failed"
                return render_template("changePassword.html", msg=msg)
            else:
                msg = "Wrong password"
        conn.close()
        return render_template("changePassword.html", msg=msg)
    else:
        return render_template("changePassword.html")

@app.route("/updateProfile", methods=["GET", "POST"])
def updateProfile():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']
        if(len(phone)!=10):
            return InvalidUsage("")
        Customer.update(firstName, lastName, address1, address2, zipcode, city, state, country, phone, email)
        return redirect(url_for('editProfile'))

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', error='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # email = request.form['email']
        # password = request.form['password']
        cust = Customer(email = email,password = password)
        if cust.status:
            session['email'] = email
            session["type"] = "cst"
            return redirect(url_for('root'))
        else:
            error = 'Invalid UserId / Password'
            return render_template('login.html', error=error)

@app.route("/productDescription")
def productDescription():
    loggedIn, firstName, noOfItems = getLoginDetails()
    productId = request.args.get('productId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT productId, name, price, description, image, stock FROM products WHERE productId = ' + productId)
        productData = cur.fetchone()
    conn.close()
    
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.lab

    cur = db.labs.find({"id":str(productId)})
    try:
        review = list(cur)[0]
    except:
        review={}
    try:
        review.pop("id")
        review.pop("_id")
    except:
        pass

    return render_template("productDescription.html", data=productData, loggedIn = loggedIn, firstName = firstName, noOfItems = noOfItems,review=json.dumps(review))


############################################################################
@app.route("/addToCart")
def addToCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        productId = int(request.args.get('productId'))
        cust = Customer(session["email"])
        cust.addcart(productId)
    
        return redirect(url_for('root'))

@app.route("/cart")
def cart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    loggedIn, firstName, noOfItems = getLoginDetails()
    cust = Customer(session["email"])
    products,totalPrice = cust.cart()
    return render_template("cart.html", products = products, totalPrice=totalPrice, loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)

@app.route("/removeFromCart")
def removeFromCart():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    productId = int(request.args.get('productId'))
    cust = Customer(session["email"])
    cust.removecart(productId)
    
    return redirect(url_for('root'))

#################################################################


@app.route("/removeFromOrders")
def removeFromOrders():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    productId = int(request.args.get('productId'))
    cust = Customer(session["email"])

    cust.removeorder(productId)
    return redirect(url_for('root'))




@app.route('/checkout')
def checkout():
    # import pdb; pdb.set_trace()
    if 'email' not in session:
        return redirect(url_for('loginForm'))

    cust = Customer(session["email"])
    try:
        data = cust.placingorder()
        return render_template("checkout.html",totalprice=data["totalprice"])
    except:
        return render_template("error.html",msg="Sorry the stocks are unavailable now :( ")




@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))



@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        address1 = request.form['address1']
        address2 = request.form['address2']
        zipcode = request.form['zipcode']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        phone = request.form['phone']

        msg = Customer.register(hashlib.md5(password.encode()).hexdigest(), email, firstName, lastName, address1, address2, zipcode, city, state, country, phone)
        return render_template("login.html", error=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")


@app.route('/sellers/login',methods=['POST', 'GET'])
def seller_login():
    return render_template('index.html')



@app.route('/sellers/orders',methods=['POST','GET'])
def ordersview():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']

        users = Seller.verify(username,password)
        if len(users)!=0:
            session["type"] = "seller"
            session["id"]=users[0][0]
            users = Seller.retrieveUsers(username,password)
            return render_template('orders.html', users=users)
        else:
            return render_template('register_seller.html')
    else:
        return "<b> Oops!!! You are not supposed to be Here  :-(. </b> "

@app.route('/sellers/update',methods=["GET","POST"])
def seller_update():
    if request.method == "GET":
        if "type" in session and session["type"] == "seller":
            admin = Admin()
            categories = admin.add()
            return render_template('update.html',categories=categories)
    if request.method == "POST":
        if "type" in session and session["type"] == "seller":
            name = request.form['name']
            price = float(request.form['price'])
            description = request.form['description']
            stock = int(request.form['stock'])
            categoryId = int(request.form['category'])

            #Uploading image procedure
            image = request.files['image']
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imagename = filename

            if "type" in session and session["type"] == "seller":
                msg = Seller.update(name, price, description, imagename, stock, categoryId)
                Seller.updatetable(name,int(session["id"]))
                return redirect(url_for('root'))

            else:
                raise InvalidUsage('Invalid Credentials', status_code=415)

    return "<b> Oops!!! You are not supposed to be Here  :-(. </b> "



@app.route('/account/orders')
def myorders():
    if "email" in session :
        #call orders
        cust = Customer(session["email"])
        orders = cust.get_order()
    loggedIn, firstName, noOfItems = getLoginDetails()
    # load html
    return render_template("manageorder.html", products = orders["products"], totalPrice=orders["price"], loggedIn=loggedIn, firstName=firstName, noOfItems=noOfItems)


def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans
