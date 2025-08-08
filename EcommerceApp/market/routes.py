import os
from crypt import methods
from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import AddItemForm, RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}



@app.route('/')
@app.route('/home')
def home_page():
    items=Item.query.filter_by()
    
    items2 = []
    for y in range(4):
        x = items[y]
        items2.append(x)
        #print(x,x.__class__,type(x))
    print(items2)
    return render_template('home.html',items=items2)
    

@app.route('/market',methods=['GET','POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        #Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$", category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!", category='danger')
        #Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')


        return redirect(url_for('market_page'))
        
    if request.method=="GET":
        items=Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html',items=items,owned_items=owned_items,c_user=current_user,purchase_form=purchase_form,selling_form=selling_form)

    return render_template('market.html',c_user=current_user)

@app.route('/Signin', methods=['GET','POST'])
def Signin_page():
    form =RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                            email_address=form.email_address.data,
                            password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully.You are logged in as {user_to_create.username}", category='success')
        return redirect(url_for('market_page'))
    return render_template('register.html',form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form= LoginForm()
    DNo=0
    vali=form.validate_on_submit()
    if form.validate_on_submit():
        #return "validate has run"
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
        attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            DNo=1
            flash('Username and password are not match! Please try again', category='danger')
            return "Username and password are not match! Please try again"
            
    return render_template('login.html',form=form)

@app.route('/item_purchase/<item_no>')
def item_purchase(item_no):
    req_item = Item.query.filter_by(id=item_no).first()
    return render_template("item_purchase.html",item = req_item)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_item', methods=['GET','POST'])
@login_required
def add_item():
    form = AddItemForm()
    if form.validate_on_submit():
        # check if the post request has the file part
        print(request)
        print(request.files)
        print(request.url)
        print( 'file' not in request.files)
        print(request.files['img'])
        print(request.files['img'].filename)
        
        if 'img' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['img']
        print(file)
        print(file.filename)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            newname = form.name.data + ".png"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], newname))
            #return redirect(url_for('market_page'))
        item_to_create = Item(name=form.name.data,
                            price =form.price.data,
                            barcode=form.barcode.data,
                            description = form.description.data)
        db.session.add(item_to_create)
        db.session.commit()
        flash(f"Item successfully added {item_to_create.name}", category='success')
        return redirect(url_for('market_page')) 
    return render_template('add_item.html',form=form)
  
@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    
    return redirect(url_for("home_page"))