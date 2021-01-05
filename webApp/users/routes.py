from flask import render_template, url_for, flash, redirect, request, Blueprint , make_response
from flask_login import login_user, current_user, logout_user, login_required
from webApp import db, bcrypt
from webApp.models import User, Post , Task , Transaction , Income, Product
from webApp.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm, TaskForm, 
                                   Sort_TaskForm, TransactionForm, Sort_Transactions, 
                                   Generate_Report, IncomeForm, Sort_Income,ProductForm , SearchProductForm)
from webApp.users.utils import save_picture, send_reset_email
import datetime as dt
from sqlalchemy import extract
import matplotlib.pyplot as plt
import pandas as pd
import base64
import math
import json
import requests
import time

from io import BytesIO

from webApp.config import Config




users = Blueprint('users', __name__)


#Registration Page
@users.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username= form.username.data , email = form.email.data , password= hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register' , form=form)


#Login Page
@users.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccesful Please check email and password', 'danger')        
    return render_template('login.html', title='Login' , form=form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))    


@users.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static' , filename= 'profile_pics/' + current_user.image_file) 
    return render_template('account.html',title='Account',
                           image_file=image_file , form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page' , 1 , type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page , per_page = 5)
    return render_template('user_posts.html',posts=posts , user=user )


@users.route("/reset_password" , methods=['GET','POST'] )
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form= RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your Password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title = 'Reset Password' , form=form)

@users.route("/reset_password/<token>" , methods=['GET','POST'] )
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)    
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been changed')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title = 'Reset Password' , form=form)                



#Finance Section ---------------------------------------------------------------------------------------------------------------------------------------------------

#Functions
def calc_TAX(amount,per):
    return amount/(100+per)*per

def sum_total(transactions):
    return sum([trans.amount for trans in transactions])



#Filters by month and year
# trans = Transaction.query.filter(extract("month", Transaction.date)==month).filter(extract('year', Transaction.date)==year).all()

#curr_month= dt.date.today().strftime("%m")

def curr_month():
    return dt.date.today().strftime("%m")
#Transaction Page where you can add and sort transactions by category and month

@users.route("/transactions/", methods=['GET','POST'])
@login_required
def transactions():
    form = TransactionForm()
    sort_form = Sort_Transactions()
    #Gets querystring arguments if none set to a default
    if request.args.get("month"):
        month = request.args.get("month")
    else:
        month = curr_month()

    if request.args.get("category"):
        category = request.args.get("category")
    else:
        category = "all"


    if sort_form.sort_submit.data and sort_form.validate_on_submit():
        return redirect(url_for('users.transactions', month=sort_form.month.data, category=sort_form.sort_category.data,  date_desc=sort_form.date_desc.data))

    if category == 'all':
        transactions = Transaction.query.filter_by(author = current_user).filter(extract("month", Transaction.date)==month).all()
        total_sum = sum_total(transactions)    
    else:        
        transactions = Transaction.query.filter_by(author = current_user , category = category).filter(extract("month", Transaction.date)==month).all()
        total_sum = sum_total(transactions)


    #Adds Transaction to the database
    if form.submit.data and form.validate_on_submit():

        tax= calc_TAX(float(form.amount.data),float(form.tax_percentage.data))

        # Transforms to BOOLEAN
        if form.is_deductable.data == "Yes":
            is_deductable = True
        else:
            is_deductable = False

        if form.category.data == 'abbonement':
            transaction = Transaction(category= form.category.data, 
            content=form.content.data, author= current_user, 
            amount=float(form.amount.data) , tax_percentage = float(form.tax_percentage.data) , tax_amount=tax, sub=True , is_deductable = is_deductable)
        else:
            transaction = Transaction(category= form.category.data, 
            content=form.content.data, author= current_user, 
            amount=float(form.amount.data) , tax_percentage = float(form.tax_percentage.data) , tax_amount=tax , is_deductable = is_deductable) 
        db.session.add(transaction)
        db.session.commit()
        flash('Added!','success')
        return redirect(url_for('users.transactions', month=curr_month(), category="all",  date_desc=0))



    return render_template('transactions.html', title='Finances' , form=form,  transactions=transactions , sort_form=sort_form , total_sum=total_sum, no_sidebar=True , curr_month=curr_month())



#Deletes a Transaction
@users.route("/transaction/<int:transaction_id>/delete", methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction= Transaction.query.get_or_404(transaction_id)
    if transaction.author != current_user:
        abort(403)
    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted!', 'success')
    return redirect(request.referrer)



#Add income
@users.route("/add_income", methods=['GET','POST'])
@login_required
def add_income():
    form = IncomeForm()
    sort_form = Sort_Income()
    if request.args.get("month"):
        month = request.args.get("month")
    else:
        month = curr_month()
    income_data = Income.query.filter_by(author = current_user).filter(extract("month", Income.date)==month).all()

    

    if form.submit.data and form.validate_on_submit():
        if form.monthly.data == "Yes":
            monthly = True
        else:
            monthly = False

        income = Income(author= current_user , company = form.company.data , source = form.source.data , amount = form.amount.data , monthly = monthly , hours_worked = form.hours_worked.data)
        db.session.add(income)
        db.session.commit()
        flash('Income Added!','success')
        return redirect(url_for('users.add_income'))


    if sort_form.sort_submit.data and sort_form.validate_on_submit():
        return redirect(url_for('users.add_income', month=sort_form.month.data))

    return render_template('add_income.html', form=form, sort_form=sort_form,  income_data=income_data, total_sum= sum_total(income_data) )

#Deletes a Income
@users.route("/income/<int:income_id>/delete", methods=['POST'])
@login_required
def delete_income(income_id):
    income= Income.query.get_or_404(income_id)
    if income.author != current_user:
        abort(403)
    db.session.delete(income)
    db.session.commit()
    flash('Income deleted!', 'success')
    return redirect(request.referrer)



#Dashboard 

@users.route("/dashboard/", methods=['GET','POST'])
@login_required
def dashboard():

    #Gets current date when page loads.
    current_date = dt.date.today()

    if request.args.get("begin"):
        begin = request.args.get("begin")
    else:
        begin = current_date.strftime('%Y-%m')+'-1'

    if request.args.get("end"):
        end = request.args.get("end")
    else:
        end = current_date.strftime('%Y-%m-%d')
    #Gets all users transactions 
    trans = Transaction.query.filter_by(author = current_user)
    

    #Checks if the current user has any transactions otherwise redirects the user to the transaction page
    if trans.count() != 0 :
        #Transform transactions into a dataframe with the date as index
        df = pd.DataFrame(vars(t) for t in trans)
        df.set_index('date', inplace= True)

        #Form for setting begin and end date
        form = Generate_Report()
        if form.submit.data and form.validate_on_submit():
            return redirect(url_for('users.dashboard',begin = form.begin.data, end= form.end.data))

        #Converts begin and end to datetime objects
        begin = dt.datetime.strptime(begin, '%Y-%m-%d')
        end = dt.datetime.strptime(end, '%Y-%m-%d')

        #We add one day so when we slice by date the end date gets included
        end = end + dt.timedelta(days=1)

        #filters out the fixed monthly costs
        filt = (df['sub'] == False)
        data = df.loc[filt][begin:end]
        data_grp = data.groupby(['category'])
        sums = data_grp.apply(lambda x: x.amount.sum())
        
        #Dict containing all info so we can pass this onto the template
        expenses = {}
        expenses['sums'] = sums
        expenses['total_sum'] = sum(expenses['sums'])
        expenses['monthly_cost'] = df.loc[df['sub'] == True, 'amount'].sum()

        #Calculates total monthly cost by subtracting end and begin taking the days and rounding the days/31.1 up to the nearest integer
        expenses['total_monthly_cost'] = expenses['monthly_cost']*math.ceil((end-begin).days/31.1)
        expenses['total'] = expenses['total_monthly_cost'] + expenses['total_sum']

        
        expenses['begin_month'] = begin.strftime('%B %Y')
        expenses['end_month'] = end.strftime('%B %Y')


                #Generates Graph
        # Generate the figure **without using pyplot**.
        fig = plt.figure()
        ax = fig.subplots()
        ax.pie(sums.values, shadow=True , startangle=90, labels=sums.index, autopct='%1.1f%%')
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        pie_plot = base64.b64encode(buf.getbuffer()).decode("ascii")


        # Gets all transaction data to generate a year plot
        df = pd.read_sql("transaction",db.engine)
        df['Date'] = pd.to_datetime(df['date'])
        df = df.loc[df['category'] != 'abbonement']
        df = df.groupby([pd.Grouper(key='date', freq='M'),'category'])

        fig, ax = plt.subplots(figsize=(6,4))
        plot = df.sum()['amount'].unstack().plot(ax=ax)
        # Save it to a temporary buffer.
        buf = BytesIO()
        fig.savefig(buf, format="png")
        # Embed the result in the html output.
        year_plot = base64.b64encode(buf.getbuffer()).decode("ascii")




        #Income data
        income_data = Income.query.filter_by(author = current_user)
        income_df = pd.DataFrame(vars(i) for i in income_data)
        income_df.set_index('date', inplace= True)

        income_df_slice = income_df[begin:end]

        income = {}

        freelance_df = income_df_slice.loc[(income_df_slice['source'] == 'Freelance')]
        income['freelance'] = {}
        income['freelance']['amount'] = freelance_df['amount'].sum()
        #Check if there is any data to calculate or it sets everyting to 0 to avoid errors same for wage
        if income['freelance']['amount'] != 0:
            income['freelance']['VAT'] = (income['freelance']['amount']/121)*21
            #Gets all transactions that are tax deductable and gets their TAX
            income['freelance']['deductable'] = data.loc[data['is_deductable'] == True, 'tax_amount'].sum()
            income['freelance']['Total_VAT'] = float(income['freelance']['VAT']) - float(income['freelance']['deductable'])
            income['freelance']['hours_worked'] = float(freelance_df['hours_worked'].sum())
            income['freelance']['net_amount'] = float(income['freelance']['amount']) - income['freelance']['Total_VAT'] 
            income['freelance']['avg_wage'] =  income['freelance']['net_amount']/income['freelance']['hours_worked']
        else:
            income['freelance']['VAT'] = 0
            #Gets all transactions that are tax deductable and gets their TAX
            income['freelance']['deductable'] = 0
            income['freelance']['Total_VAT'] = 0
            income['freelance']['hours_worked'] = 0
            income['freelance']['net_amount'] = 0
            income['freelance']['avg_wage'] =  0


        wage_df = income_df_slice.loc[(income_df_slice['source'] == 'Wage')]    
        income['wage'] = {}
        income['wage']['amount'] = float(wage_df['amount'].sum())
        if income['wage']['amount'] != 0:
            income['wage']['hours_worked'] = wage_df['hours_worked'].sum()
            income['wage']['avg_hours'] = float(income['wage']['hours_worked'])/((end-begin).days/30.44)
        else:
            income['wage']['hours_worked'] = 0
            income['wage']['avg_hours'] = 0            

        income['other'] = {}
        income['other']['monthly'] = income_df.loc[(income_df['monthly'] == True)]['amount'].sum()
        income['other']['total_monthly'] = income['other']['monthly']*math.ceil((end-begin).days/31.1)
        income['other']['amount'] = income_df_slice.loc[(income_df_slice['source'] == 'Other') & (income_df_slice['monthly'] == False)]['amount'].sum()

        income['total'] = income['freelance']['net_amount'] + income['wage']['amount'] + float(income['other']['total_monthly']) + float(income['other']['amount'])

        total = income['total'] - float(expenses['total'])

        return render_template('dashboard.html' , title='Dashboard' , expenses=expenses , income=income , total=total, form=form , pie_plot=pie_plot , year_plot=year_plot, current_date=current_date, no_sidebar=True)   
    else:
        flash("Please add some transactions first before accessing the dashboard",'danger')
        return redirect(url_for('users.transactions', month=curr_month(), category="all", date_desc=0))








# END FINANCE SECTION -----------------------------------------------------------------------



# FOUENITURENEWEB TIJDELIJK  

# Remove links , add metafields, pretty the page, make searchbar link , 

@users.route("/find_product/<searchterm>", methods=['GET','POST'])
def find_product(searchterm):
    p = Product.query.filter(Product.handle.contains( searchterm )).all()[0]
    return redirect(url_for("users.update_product", product_id = p.product_id ))    

@users.route("/overview_products", methods=['GET','POST'])
def overview_products():
        products = Product.query.filter_by(completed=False)
        still_left = products.count()
        selection = products[0:15]
        form= SearchProductForm()

        if  form.submit.data and form.validate_on_submit:
            try:
                return redirect(url_for("users.find_product", searchterm = form.searchphrase.data))
            except:
                flash('That product could not be found', category='error')
                return redirect(url_for('users.overview_products'))    

        return render_template('overview_products.html', no_sidebar=True, still_left=still_left,selection=selection, form=form)

@users.route("/update_product/<int:product_id>", methods=['GET','POST'])
def update_product(product_id):
    base_url = Config.FOURNITUREN_API_BASE_URL +'/admin/api/2021-01/products/'
    
    url = base_url + str(product_id)  +'.json'
    meta_url = base_url + str(product_id) + '/metafields.json'

    r = requests.get(url).content
    data = json.loads(r)

    #time.sleep(0.5)
    #Metafield info
    r_meta= requests.get(meta_url).content
    data_meta = json.loads(r_meta)

    metafields = data_meta['metafields']

    try:
        shortDescription = [dic['value'] for dic in metafields if dic['key'] == 'shortDescription'][0]
    except:
        shortDescription = ''

    try:
        levertijd = [dic['value'] for dic in metafields if dic['key'] == 'levertijd'][0]
    except:
        levertijd = ''    

    try:
        fabriek = [dic['value'] for dic in metafields if dic['key'] == 'fabriek'][0]
    except:
        fabriek = ''

    try:
        minimum_info = [dic['value'] for dic in metafields if dic['key'] == 'aantal-tonen'][0]
    except:
        minimum_info = ''





    product = data['product']
    description = product['body_html']


    image_url = product['image']['src']

    try:
        second_image = product['images'][1]['src']
    except:
        second_image = ''

    variants  = product['variants']


    var = []
    for v in variants:
        var.append( {'variant_id':v['id'], 'option1':v['option1'] , 'option2':v['option2'] })
        
    p = Product.query.filter_by(product_id=product_id)[0]
    
    #form stuff

    form = ProductForm(variants=var)


    if  form.submit.data and form.validate_on_submit:
        updated_var = []
        for field in form.variants:
            updated_var.append( {'id':field.variant_id.data, "inventory_quantity": int(field.stock.data), "inventory_policy": "continue" })
       
        metafields = [ ]

        if form.preorder.data:
            metafields.append({
            'key': 'preorder',
            'value': form.preorder.data,
            'value_type': 'string',
            'namespace': 'preorder',
        })

        if form.quantity.data:
            metafields.append({
            'key': 'quantity',
            'value': int(form.quantity.data),
            'value_type': 'integer',
            'namespace': 'quantity',
        })

        if form.qty_steps.data:
            metafields.append({
            'key': 'qty_steps',
            'value': int(form.qty_steps.data),
            'value_type': 'integer',
            'namespace': 'qty_steps',
        })

        
        payload = {
        "product": {
                    "id": product_id,
                    "variants": updated_var,
                    "vendor": str(fabriek),
                    "metafields" : metafields

            }
        }

        if form.beschrijving.data:
            payload['product']['body_html'] = """<p style="font-size: 18px;">"""+form.beschrijving.data+"</p>"

        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        response = requests.put(url, headers=headers,  json=payload)

        if response.status_code == 200:
            flash('Product updated successfully', category='success')
            p.completed = True
            db.session.add(p)
            db.session.commit()
            return redirect(url_for("users.overview_products"))
            
        else:
            flash('Something went wrong'+str(response.content), category='error')
            return redirect(request.referrer)
        
        


    


    return render_template('update_product.html',no_sidebar=True, shortDescription=shortDescription, levertijd =levertijd ,fabriek=fabriek , minimum_info=minimum_info ,image_url=image_url,
        second_image=second_image , variants=variants , form=form , description=description, p=p
        )


