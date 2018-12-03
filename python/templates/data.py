

from flask import Flask
import sqlite3
from flask import g

app = Flask(__name__)
@app.before_request
def before_request():
    g.db = sqlite3.connect("db1.db")


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def hello_world():
    g.db.execute("INSERT INTO customer VALUES 'name'")
    g.db.commit()


if __name__ == '__main__':
    app.run()

