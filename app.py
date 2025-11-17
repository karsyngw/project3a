import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True



# Function to open a connection to the database.db file
def get_db_connection():
    # create connection to the database
    conn = sqlite3.connect('database.db')
    
    # allows us to have name-based access to columns
    # the database connection will return rows we can access like regular Python dictionaries
    conn.row_factory = sqlite3.Row

    #return the connection object
    return conn


# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    
    return "<h1>Welcome to My Blog</h1>"


# route to create a post


app.run()