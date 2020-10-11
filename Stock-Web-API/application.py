from flask import Flask
from flask import request
from flask import render_template
from flask import send_file
from flask import jsonify
import json
import requests
from datetime import *
from dateutil.relativedelta import *


application = Flask(__name__, static_url_path='', static_folder='static')

@application.route('/', methods = ['GET', 'POST'])
def index():
    return application.send_static_file('main_page.html')
        

@application.route('/todo/api/v1.0/todo/<string:value>', methods = ['GET'])
def search(value):
    keyword = value
    # get the stock-sticker-symbol (keyword) from javascript 

    # API key for a particular user is constant 
    API_KEY = "3011052a592245558538c1c7a73ca77f0552c7a5" 
    
    try:
        # Step 1: Company Outlook
        # Calling tiingo meta endpoint API
        requestResponse1 = requests.get("https://api.tiingo.com/tiingo/daily/" + keyword.lower() + "?token=" + API_KEY, headers={'Content-Type': 'application/json'})
        tmp = requestResponse1.json()
        # Store Values
        tab1 = {}
        tab1['company_name'] = tmp['name'] if tmp['name'] else ""
        tab1['stock_ticker_symbol'] = tmp['ticker'] if tmp['ticker'] else ""
        tab1['stock_exchange_code'] = tmp['exchangeCode'] if tmp['exchangeCode'] else ""
        tab1['company_start_date'] = tmp['startDate'][:10] if tmp['startDate'] else ""
        tab1['description'] = tmp['description'] if tmp['description'] else "" # Limit to 5 lines
        # print('TAB 1 DONE')
        # Step 2: Stock Summary
        # Calling tiingo Current Top-of-Book & Last Price API
        
        requestResponse2 = requests.get("https://api.tiingo.com/iex/" + keyword.lower() + "?token=" + API_KEY, headers={'Content-Type': 'application/json'} )
        data = requestResponse2.json()[0]
        
        tab2  = { 'stock_ticker_symbol': tab1['stock_ticker_symbol'] }
        tab2['trading_day'] = data['timestamp'][:10] if data['timestamp'] else ""
        tab2['previous_closing_price'] = data['prevClose'] if data['prevClose'] else ""
        tab2['opening_price'] = data['open'] if data['open'] else ""
        tab2['high_price'] = data['high'] if data['high'] else ""
        tab2['low_price'] = data['low'] if data['low'] else ""
        tab2['last_price'] = data['last'] if data['last'] else ""
        tab2['change'] = round(tab2['last_price'] - tab2['previous_closing_price'], 2) if tab2['last_price'] else ""  # Display Arrow
        tab2['change_percent'] = round((tab2['change']/tab2['previous_closing_price']) * 100, 2) if tab2['change'] else "" # Display Arrow
        tab2['no_shares_traded'] = data['volume'] if data['volume'] else ""
        # print('TAB 2 DONE')

        # Step 3: Chart Data 
        # Calling the  Tiingo Historical Intraday Prices Endpoint API
        startDate = date.today() + relativedelta(months=-6)
        hours = 12
        requestResponse3 = requests.get('https://api.tiingo.com/iex/' + keyword.lower() + '/prices?startDate=' +  str(startDate) + '&resampleFreq=' + str(hours) + 'hour&columns=open,high,low,close,volume&token=' + API_KEY, headers={'Content-Type': 'application/json'})
        tab3 = { 'dp': [],
                 'dv': []} 

        for val in requestResponse3.json():
            tab3['dp'].append({'date': val['date'][:10], 'price': val['close']})
            tab3['dv'].append({'date': val['date'][:10], 'volume': val['volume']})  
        # print('TAB 3 DONE')

        # Step 4: Calling the News API
        # using news api
        NEWS_API_KEY = 'bfd84969d428492eb0dfbadc77215fe1'
        requestResponse4 = requests.get('https://newsapi.org/v2/everything?apiKey=' + NEWS_API_KEY + '&q=' + keyword.lower(), headers={'Content-Type': 'application/json'})
        # print(requestResponse4.json())
        tab4 = {'0': {}, '1': {}, '2': {}, '3': {}, '4': {}}

        count = 0
        temp = requestResponse4.json()['articles']
        for i, val in enumerate(temp):
            x = temp[i]
            if x['title'] and x['url'] and x['urlToImage'] and x['publishedAt'] and count < 5:
                tab4[str(count)]['image'] = x['urlToImage']
                tab4[str(count)]['title'] = x['title']
                tab4[str(count)]['date'] = x['publishedAt'][:10]
                tab4[str(count)]['link'] = x['url']
                count += 1
        # print('TAB 4 DONE')

        
        
        return jsonify(tab1 = tab1,
                       tab2 = tab2,
                       tab3 = tab3,
                       tab4 = tab4)

    except:
        # print('ERROR')
        return "{}"
    
    
	

if __name__ == '__main__':
	application.debug = False
	application.run()










