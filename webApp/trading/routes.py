'''
Disabled

from flask import render_template, url_for, flash, redirect, request, Blueprint , make_response
from flask_login import login_user, current_user, logout_user, login_required
from webApp import db, bcrypt
from webApp.models import StockAlert
from webApp.config import Config
import ast, requests, json
import logging
import datetime as dt
#Connect to the api
url = "https://paper-api.alpaca.markets"
key = Config.ALPACA_PAPER_KEY_ID
secret_key = Config.ALPACA_PAPER_SECRET_KEY
HEADERS = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret_key}

#Exchange info


NASDAQ_OPEN = dt.time(15, 30) #15:30 (GMT+2)
NASDAQ_CLOSE = dt.time(22) # 22:00 (GMT+2)


trading = Blueprint('trading', __name__)


#Remove this functionality and remove the saving of the triggers

@trading.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == "POST":
        #Takes the webhook data as a string and converts it into dictionary
        data = ast.literal_eval(request.get_data(as_text=True))
        stockalert = StockAlert(high_price=data['high'], close_price= data['close'], low_price= data['low'] , exchange = data['exchange'], ticker=data['ticker'], open_price = data['open'], volume= data['volume'])
        
        #Add to database
        db.session.add(stockalert)
        db.session.commit()
        url_for('trading.buy_stock', qty=1, ticker=stockalert.ticker, price=stockalert.high_price, take_profit=stockalert.high_price*1.02, stop_price= stockalert.high_price*0.98)

       

    alerts = StockAlert.query.all()    
    return render_template('webhook.html', alerts = alerts, no_sidebar=True)


@trading.route('/paper/dashboard')
def paper_wallet():


    #Get account info
    r = requests.get(f"{url}/v2/account", headers=HEADERS)
    account_info = json.loads(r.content)

    positions = json.loads(requests.get(f"{url}/v2/positions", headers=HEADERS).content)

    for pos in positions:
        pos['unrealized_plpc'] = float(pos['unrealized_plpc'])* 100

 
    return render_template('trading_dashboard.html', account_info=account_info, positions = positions, no_sidebar=True)


@trading.route('/paper/buy-stock', methods=['POST'])
def buy_stock():

    if request.method == "POST":
        #Takes the webhook data as a string and converts it into dictionary
        data = ast.literal_eval(request.get_data(as_text=True))
        ticker = data['ticker']
        price = data['close']


        qty = 1
        order_info =  {
            "symbol": ticker,
            "qty": qty,
            "side": "buy",
            "type": "market",
            "time_in_force": "gtc",
            "order_class": "bracket",
            "take_profit": {
                "limit_price": price * 1.05
            },
            "stop_loss": {
                "stop_price": price * 0.98,
            }
        }
        r = requests.post(f"{url}/v2/orders", headers=HEADERS, json=order_info)
        response = json.loads(r.content)
        return "OK"
    else:
        return url_for('trading.paper_wallet')


'''
