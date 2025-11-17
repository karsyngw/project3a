import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

import csv
import pygal
import datetime
import requests

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'
stocks_csv = "stocks.csv"

#Dropdown menu to select stock symbol
def get_stock_symbols():
    stock_symbols = []
    with open(stocks_csv, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # skip header row
        for row in csvreader:
            stock_symbols.append(row[0])
    return stock_symbols

#creates chart based on information provdied by user
def make_chart(start_date, end_date, data, chart_type):
    #Checks API for data availablity from given values and grabs data from API
    key = next((k for k in data.keys() if "Time Series" in k), None)
    if not key:
        return None
    #Assigns data to time_series 
    time_series = data[key]
    #Filter data between start_date and end_date
    open_data = {}
    high_data = {}
    low_data = {}
    close_data = {}
    for date_str, values in time_series.items():
        try:
            #Detect whether intraday or not
            if " " in date_str:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                date_only = date_obj.date()
            else:
                date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                date_only = date_obj.date()

            #Filter by date range (compare dates only)
            #separates the data into open, close, high, and low
            if start_date <= date_only <= end_date:
                open_data[date_obj] = float(values['1. open'])
                high_data[date_obj] = float(values['2. high'])
                low_data[date_obj] = float(values['3. low'])
                close_data[date_obj] = float(values['4. close'])

        except Exception:
            continue
    if not close_data:
        return None
    # Sort by date
    high_data = dict(sorted(high_data.items()))
    low_data = dict(sorted(low_data.items()))
    open_data = dict(sorted(open_data.items()))
    close_data = dict(sorted(close_data.items()))
    #Create chart based on user chart choice
    #Line chart
    if chart_type == 'Line':
        chart = pygal.Line()
        chart.title = "Stock Prices"
        chart.x_labels = [d.strftime('%Y-%m-%d') for d in close_data.keys()]
        chart.add("Open", list(open_data.values()))
        chart.add("High", list(high_data.values()))
        chart.add("Low", list(low_data.values()))
        chart.add("Close", list(close_data.values()))
        return chart
    #Bar chart
    elif chart_type == 'Bar':
        chart = pygal.Bar()
        chart.title = "Stock Prices"
        chart.x_labels = [d.strftime('%Y-%m-%d') for d in close_data.keys()]
        chart.add("Open", list(open_data.values()))
        chart.add("High", list(high_data.values()))
        chart.add("Low", list(low_data.values()))
        chart.add("Close", list(close_data.values()))
        return chart

#home page
@app.route('/', methods=('GET', 'POST'))
def index():
    stock_symbols = get_stock_symbols()
    selected_stock = None
    chart_type = None
    time_series = None
    start_date = None
    end_date = None
    chart = None
    stock_chart = None

    if request.method == 'POST':
        #gets the information from the form in index.html 
        #checks to make sure all of the needed data is there and flashes error message is missing
        selected_stock = request.form['symbol']
        if not selected_stock:
            flash("ERROR: Must select a stock symbol")
        chart_type = request.form['chart']
        if not chart_type:
            flash("ERROR: Must select a chart type")
        time_series = request.form['time_series']
        if not time_series:
            flash("ERROR: Must select a time series function")
        if(time_series == "Intraday"):
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={selected_stock}&interval=5min&apikey=ZI4OPB83KP5Q1JNR'
        elif(time_series == "Daily"):
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={selected_stock}&apikey=ZI4OPB83KP5Q1JNR'
        elif(time_series == "Weekly"):
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={selected_stock}&apikey=ZI4OPB83KP5Q1JNR'
        elif(time_series == "Monthly"):
            url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={selected_stock}&apikey=ZI4OPB83KP5Q1JNR'
            
        start_date = request.form['start_date']
        if not start_date:
            flash("ERROR: Must select a start date")
        start_date_datetime = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = request.form['end_date']
        if not end_date:
            flash("ERROR: Must select an end date")
        end_date_datetime = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        if end_date_datetime < start_date_datetime:
            flash("ERROR: End date must be after start date")
            return redirect(url_for('index'))

        #gets the data from the api
        r = requests.get(url)
        data = r.json()

        #makes chart using make chart function and flashes an error message in anything goes wrong
        chart = make_chart(start_date_datetime, end_date_datetime, data, chart_type)
        if chart is None:
            flash("ERROR: No valid time series data found")
            return redirect(url_for('index'))
        
        stock_chart = chart.render_data_uri()

    return render_template('index.html', stock_symbols=stock_symbols, chart=stock_chart, selected_stock=selected_stock, start_date=start_date, end_date=end_date)

app.run(host="0.0.0.0")