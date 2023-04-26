from flask import Flask, render_template, request, session, redirect, url_for
from sqlalchemy import create_engine, text, select, Table, Column, Integer, String, MetaData

app = Flask(__name__)
app.secret_key = ''
conn_str = "mysql://root:@localhost/Final_Project"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
