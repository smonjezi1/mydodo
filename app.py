import pandas as pd
import io
import requests
from datetime import date
from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure, show, output_notebook
from bokeh.embed import components
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Range1d

app = Flask(__name__)

#Quandle API key
mykey = "MyKey"

#data from the begining of 2018 instead of a month ago because quandle is not updated after April
quandl_url_left = "https://www.quandl.com/api/v3/datasets/WIKI/"
quandl_url_right = ".csv?column_index=4&start_date=2018-01-01&api_key="

#returns closing price data
def fun_df_close(tckr_id):
    url = quandl_url_left + tckr_id + quandl_url_right + mykey
    s = requests.get(url).content
    try:
        df_close = pd.read_csv(io.StringIO(s.decode('utf-8')))
        df_close['Date'] = pd.to_datetime(df_close['Date'])
    except:
        df_close=pd.DataFrame()       
    return df_close

# returns bokeh figure
def fun_bokeh(df_close, tckr_id):
    bokeh_fig = figure(width=1000, height=500, title=tckr_id.upper())
    bokeh_src = ColumnDataSource(df_close)
    bokeh_fig.line('Date', 'Close', source = bokeh_src)
    bokeh_fig.xaxis.formatter=DatetimeTickFormatter(days=["%d %b"])
    bokeh_fig.x_range=Range1d(df_close['Date'].min(), df_close['Date'].max())
    bokeh_fig.yaxis.axis_label = "Closing price"
    
    return bokeh_fig


@app.route('/')
def main():
    return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
    err_msg = '<div class="error">\n  <p>Ticker symbol is not recognized. Please retry with a correct ticker.</p>\n</div>\n'
    if request.method == 'GET':
        return render_template('index.html', script_1="", script_2="")
    else:
        tckr_id = request.form['tckr_symbl']
        df_close = fun_df_close(tckr_id)
        if df_close.empty:
            return render_template('index.html', script_1="", script_2=err_msg)
        bokeh_fig = fun_bokeh(df_close, tckr_id)
        bokeh_scrpt_1, bokeh_scrpt_2 = components(bokeh_fig)
        return render_template(
            'index.html',
            script_1=bokeh_scrpt_1,
            script_2=bokeh_scrpt_2)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
