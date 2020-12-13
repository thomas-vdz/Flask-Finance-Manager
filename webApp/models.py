from datetime import datetime
from webApp import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    #db Links to other models 
    posts = db.relationship('Post', backref='author', lazy=True)
    tasks = db.relationship('Task', backref='author', lazy=True)
    transactions = db.relationship('Transaction', backref='author', lazy=True)
    income =  db.relationship('Income', backref='author', lazy=True)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'] , expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"

class Theorem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    chapter = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    theorem_latex = db.Column(db.Text, nullable=False)
    proof_latex = db.Column(db.Text)
    hint = db.Column(db.Text)
    difficulty = db.Column(db.String(100), nullable=False)
    progress = db.Column(db.String(100))
    
    
    def __repr__(self):
        return f"Theorem('{self.title}','{self.date_posted}')"



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.String(20))
    content = db.Column(db.String(100), nullable=False)
    importance = db.Column(db.String(3), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Task('{self.content}','{self.date_posted}')"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    tax_percentage = db.Column(db.Integer, default=21)
    amount = db.Column(db.Numeric(10,2))
    sub = db.Column(db.Boolean, default=False)
    is_deductable = db.Column(db.Boolean, default=False)
    tax_amount= db.Column(db.Numeric(10,2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Transaction('{self.amount}','{self.content}','{self.date}')"


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10,2))
    monthly = db.Column(db.Boolean, default=False)
    company = db.Column(db.String(100))
    hours_worked = db.Column(db.Numeric(10,2))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    def __repr__(self):
        return f"Income('€{self.amount} ','{self.company}  ','{self.date}')" 


class StockAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    low_price = db.Column(db.Numeric(10,2))
    high_price = db.Column(db.Numeric(10,2))
    open_price = db.Column(db.Numeric(10,2))
    close_price = db.Column(db.Numeric(10,2))
    volume = db.Column(db.Numeric(10,2))
    exchange = db.Column(db.String(100))
    ticker = db.Column(db.String(20))