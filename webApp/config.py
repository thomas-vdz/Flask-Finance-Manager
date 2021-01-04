import os 
import json

if os.name == 'nt':
    try:
        with open("C:\\Users\\thoma\\Desktop\\config.json") as config_file:
            config = json.load(config_file)
    except:
        with open("C:\\Users\\Fred\\Desktop\\config.json") as config_file:
            config = json.load(config_file)            
else:    
    with open('/etc/config.json') as config_file:
    	config = json.load(config_file)
class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER ='smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = config.get('GMAIL')
    MAIL_PASSWORD = config.get('GMAIL_PASS')
    ALPACA_PAPER_KEY_ID = config.get('ALPACA_PAPER_KEY_ID')
    ALPACA_PAPER_SECRET_KEY = config.get('ALPACA_PAPER_SECRET_KEY')
    FOURNITUREN_API_BASE_URL = config.get('FOURNITUREN_API_BASE_URL')