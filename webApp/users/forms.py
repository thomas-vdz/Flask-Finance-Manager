from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField , SelectField , RadioField, DecimalField , DateField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from webApp.models import User
from datetime import date
class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign up')
    def validate_username(self, username):       
        user = User.query.filter_by(username=username.data).first()    
        if user:
            raise ValidationError('That username is taken. Please choose a different one ')
    def validate_email(self, email):       
        user = User.query.filter_by(email=email.data).first()    
        if user:
            raise ValidationError('That email is taken. Please choose a different one ')


class LoginForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture' , validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
    
    def validate_username(self, username): 
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()    
            if user:
                raise ValidationError('That username is taken. Please choose a different one ')
    def validate_email(self, email):      
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()    
            if user:
                raise ValidationError('That email is taken. Please choose a different one ')


class RequestResetForm(FlaskForm):
    email = StringField('Email', 
                        validators=[DataRequired(), Email()])    
    submit = SubmitField('Request Password Reset')
    def validate_email(self, email):       
        user = User.query.filter_by(email=email.data).first()    
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset password')    


#Tasks
class TaskForm(FlaskForm):
    due_date = StringField('Due Date', validators=[DataRequired()])
    content = StringField('Content',  validators=[DataRequired()])
    category = SelectField('Category', choices=[('school','School'),('work','Work'),('website','Website'),('other','Other')] , default='website')
    importance = RadioField('Importance', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], default = '1')
    submit = SubmitField('Post')

class Sort_TaskForm(FlaskForm):
    sort_category = SelectField('Category:', choices=[('all','All'),('school','School'),('work','Work'),('website','Website'),('other','Other')] , default='all')
    date_desc = RadioField('Sort Date', choices=[('0','&#x2191'),('1','&#x2193')] , default='0')
    imp_desc= RadioField('Importance', choices=[('0','&#x2191'),('1','&#x2193')] , default='0')
    sort_submit = SubmitField('Sort')



#Current Date
today = date.today()
this_month = today.strftime("%m")
this_year = today.strftime("%y")
#Finance
class TransactionForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()])
    content = StringField('Content',  validators=[DataRequired()])
    category = SelectField('Category',  choices=[('Groceries','Groceries'),('Bars/Clubs','Bars/Clubs'),('Restaurants','Restaurants'),('Smoking','Smoking'),('Transportation','Transportation'),('Other','Other'),('Fixed Monthly Cost','Fixed Monthly Cost')] , default='Groceries' )
    tax_percentage = RadioField('TAX %', choices=[('21','21%'),('9','9%'),('0','0%')], default='21')
    is_deductable = RadioField('Tax Deductable?', choices=[('Yes','Yes'),('No','No')], default='No')
    submit = SubmitField('Post')

class IncomeForm(FlaskForm):
    company = StringField('Company',  validators=[DataRequired()])
    source = SelectField('Source', choices=[('Freelance','Freelance'),('Wage','Wage'),('Other','Other')] , default='Freelance')
    monthly = RadioField('Monthly?', choices=[('Yes','Yes'),('No','No')], default = 'No')
    amount = DecimalField('Amount', validators=[DataRequired()])
    hours_worked = DecimalField('Hours Worked', validators=[DataRequired()])
    submit = SubmitField('Add')


months = [("01","January"),("02","Februari"),("03","March"),("04","April"),("05","May"),("06","Juni"),("07","Juli"),("08","August"),("09","September"),("10","Oktober"),("11","November"),("12","December"),('all','All')]
years = [("2021","2021"),("2022","2022"),("2023","2023"),("2024","2024"),("2025","2025")]
class Sort_Transactions(FlaskForm):
    month = SelectField('Month:',choices=months, default = this_month)
    year = SelectField('Year:',choices=years, default = this_year)
    category = SelectField('Category:',choices=[('all','All'),('Groceries','Groceries'),('Bars/Clubs','Bars/Clubs'),('Restaurants','Restaurants'),('Smoking','Smoking'),('Transportation','Transportation'),('Other','Other')] , default='all')
    sort_submit = SubmitField('Sort')


class Sort_Income(FlaskForm):
    month = SelectField('Month:',choices=months, default = this_month)
    sort_submit = SubmitField('Sort')

class Generate_Report(FlaskForm):
    begin = StringField('Begin Date', validators=[DataRequired()])
    end = StringField('End Date', validators=[DataRequired()])
    submit = SubmitField('Generate Report')




#FOURNITURENWEB

class StockEntryForm(FlaskForm):
    variant_id = StringField()
    option1 = StringField()
    option2 = StringField()
    stock = StringField(default = '0')

class ProductForm(FlaskForm):
    """A form for one or more addresses"""
    variants = FieldList(FormField(StockEntryForm), min_entries=1)
    preorder = StringField('Levertijd' )
    quantity = StringField('Minimaal aantal')
    qty_steps = StringField('Stappen van')

    beschrijving = StringField('Beschrijving')
    submit = SubmitField('Update product')

class SearchProductForm(FlaskForm):
    searchphrase = StringField("Product id")
    submit = SubmitField('Search')