from flask import Flask, render_template, url_for, request, redirect, flash, session, make_response, jsonify
import sqlalchemy
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
import os, glob
from werkzeug.utils import secure_filename
import random
import json

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "lkkajdghdadkglajkgajdisa931!.hl" # a secret key for your app
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')

class TrAcc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')
    passcode = db.Column(db.String(6), default = '')
    assigned_students = db.relationship('StdAcc', backref="assigned_teacher")

class StdAcc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')
    assigned_teacher_id = db.Column(db.Integer, db.ForeignKey('tr_acc.id'))

class Record_Of_Items(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    cat = db.Column(db.String(200),default = '-')
    image = db.Column(db.String(200),default = '')
    quantifier = db.Column(db.String(200),default='')
    promo_price = db.Column(db.Integer,default = '-')
    

class Temporary_Table(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    acc = db.Column(db.String(200),default = '-')
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    quantity = db.Column(db.Integer,default = 1)
    cat = db.Column(db.String(200),default = '-')
    promo_price = db.Column(db.Integer,default = '-')

class Submitted_Cart(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    acc = db.Column(db.String(200),default = '-')
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    quantity = db.Column(db.Integer,default = 1)
    cat = db.Column(db.String(200),default = '-')

class Generated_Codes(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    code = db.Column(db.String(100), default = '')

random_number_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/update/<int:id>', methods = ['POST', 'GET'])
def update(id):
    if 'admin' in session:
        item = Record_Of_Items.query.get_or_404(id)
        if request.method == "POST":
            if item == None:
                return redirect('/additems')
            item.name = request.form['itemname']
            item.price = request.form['itemprice']
            item.info = request.form['iteminfo']
            item.cat = request.form['itemcat']
            item.quantifier = request.form['itemquantifier']
            try:
                db.session.commit()
                return redirect('/marketplace')
            except:
                return 'There was an issue updating your task.'
        else:
            return render_template("edititems.html", item = item)
    else:
        return redirect('/login')

@app.route('/generatecode', methods = ['POST', 'GET'])
def generate_code():
    if request.method == 'POST':
        if request.form['forest'] == 'generate':
            temp_code = []
            for i in range(6):
                random_character = random.choice(random_number_list)
                temp_code.append(random_character)
            generated_code =  str(''.join(temp_code))
            locate_code = db.session.query(TrAcc).filter_by(name = session['teacher']).first()
            locate_code.passcode = generated_code
            db.session.commit()
            return render_template('passcodepage.html', passcode = generated_code)
        else:
            generated_code = ''
            locate_code = db.session.query(TrAcc).filter_by(name = session['teacher']).first()
            locate_code.passcode = ''
            db.session.commit()
            return render_template('passcodepage.html', passcode = generated_code)
    else:
        return redirect('/login')

@app.route('/newacc', methods=['POST', 'GET'])
def createacc():
    #render_template for creating acc
    if request.method == 'POST':
        new_acc_user = request.form['usertype']
        new_acc_name = request.form['username']
        new_acc_pword = request.form['password']
        if new_acc_user == 'AdminUser':
            check = Admin.query.filter_by(name=new_acc_name, pword=new_acc_pword).first()
            if check == None:
                new_acc = Admin(name = new_acc_name, pword = new_acc_pword)
                db.session.add(new_acc)
                db.session.commit()
                return "success AdminAcc creation"
        elif new_acc_user == 'TeacherUser':
            check1 = TrAcc.query.filter_by(name=new_acc_name, pword=new_acc_pword).first()
            if check1 == None:
                new_acc = TrAcc(name = new_acc_name, pword = new_acc_pword)
                db.session.add(new_acc)
                db.session.commit()
                return render_template('addteachers.html', feedback = "Successful Teacher Account Creation.")
            else:
                return render_template('addteachers.html', feedback = "Teacher Account already exists.")
        elif new_acc_user == 'StudentUser':
            check2 = StdAcc.query.filter_by(name=new_acc_name, pword=new_acc_pword).first()
            if check2 == None:
                assigned_teacher_name = request.form['Teacher']
                assigned_teacher = db.session.query(TrAcc).filter_by(name = assigned_teacher_name).first()
                new_acc = StdAcc(name = new_acc_name, pword = new_acc_pword, assigned_teacher = assigned_teacher)
                db.session.add(new_acc)
                db.session.commit()
                teachers = db.session.query(TrAcc)
                return render_template('addstudents.html', feedback = "Successful Student Account Creation.", teachers = teachers)
            else:
                teachers = db.session.query(TrAcc)
                return render_template('addstudents.html', feedback = "Student Account already exists.", teachers = teachers)

@app.route('/wipedb', methods =['POST', 'GET'])
def wipedb():
    if 'admin' in session:
        return render_template('wipedbpage.html')
    else:
        redirect('/login')

@app.route('/removeallobjects', methods = ['POST', 'GET'])
def removeallobjects():
    if 'admin' in session:
        if request.method == 'POST':
            if request.form['page'] == 'wipedbpage':
                if request.form['objectss'] == 'removeallstudents':
                    db.session.query(StdAcc).delete()
                    db.session.commit()
                    return redirect('/wipedbpage')
                elif request.form['objectss'] == 'removeallteachers':
                    db.session.query(TrAcc).delete()
                    db.session.commit()
                    return redirect('/wipedbpage')
                elif request.form['objectss'] == 'removeallitems':
                    db.session.query(Record_Of_Items).delete()
                    db.session.commit()
                    for file in glob.glob("static/uploads/*"):
                        os.remove(file)
                    return redirect('/wipedbpage')
                elif request.form['objectss'] == 'removeallsubmitted':
                    db.session.query(Submitted_Cart).delete()
                    db.session.commit()
                    return redirect('/wipedbpage')
                elif request.form['objectss'] == 'removeallcurrent':
                    db.session.query(Temporary_Table).delete()
                    db.session.commit()
                    return redirect('/wipedbpage')
            else:
                if request.form['objectss'] == 'removeallstudents':
                    db.session.query(StdAcc).delete()
                    db.session.commit()
                    return redirect('/tablestudent')
                elif request.form['objectss'] == 'removeallteachers':
                    db.session.query(TrAcc).delete()
                    db.session.commit()
                    return redirect('/tableteacher')
                elif request.form['objectss'] == 'removeallitems':
                    db.session.query(Record_Of_Items).delete()
                    db.session.commit()
                    return redirect('/marketplace')
                elif request.form['objectss'] == 'removeallsubmitted':
                    db.session.query(Submitted_Cart).delete()
                    db.session.commit()
                    return redirect('/marketplace')
                elif request.form['objectss'] == 'removeallcurrent':
                    db.session.query(Temporary_Table).delete()
                    db.session.commit()
                    return redirect('/marketplace')
        else:
            return redirect('login')
    else:
        return redirect('/login')


@app.route('/reinitialisedb', methods = ['POST', 'GET'])
def reinitialisedb():
    if 'admin' in session:
        db.session.query(TrAcc).delete()
        db.session.query(StdAcc).delete()
        #all_codes = db.session.query(Generated_Codes).all()
        #for code in all_codes:
        #    code.code = ''
        db.session.query(Record_Of_Items).delete()
        db.session.query(Temporary_Table).delete()
        db.session.query(Submitted_Cart).delete()
        db.session.commit()
        return redirect('/admin')
    else:
        return redirect('/login')

@app.route('/display/<filename>', methods = ['POST', 'GET'])
def display_image(filename):
    return redirect(url_for('static', filename = 'uploads/' + filename), code = 301)

@app.route('/testadd', methods=['POST', 'GET'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        image_file = request.files['file']
        if image_file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_file = Record_Of_Items(image = filename)
            db.session.add(new_file)
            db.session.commit()
            return render_template('testadd.html', filename=filename)
        else:
            flash('Allowed image types are -> png, jpg, jpeg, gif')
            return redirect(request.url)
    else:
        return render_template('testadd.html')

@app.route('/additems', methods=["POST", 'GET'])
def additems():
    if 'admin' in session:
        all_items_categories = db.session.query(Record_Of_Items)
        categories = []
        for cate in all_items_categories:
            categories.append(cate.cat)
        legit_categories = set(categories)
        if request.method == 'POST':
            new_item_name = request.form['itemname']
            new_item_price = request.form['itemprice']
            new_item_info = request.form['iteminfo']
            new_item_cat = request.form['itemcat']
            new_item_quantifier = request.form['itemquantifier']
            new_item_image = request.files['itemimage']
            check = Record_Of_Items.query.filter_by(name=new_item_name).first()
            if check == None:
                if new_item_image and allowed_file(new_item_image.filename):
                    filename = secure_filename(new_item_image.filename)
                    new_item_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                else:
                    filename = None
                new_item = Record_Of_Items(name = new_item_name, price = new_item_price, info = new_item_info, cat = new_item_cat, quantifier = new_item_quantifier, image = filename)
                db.session.add(new_item)
                db.session.commit()
                return render_template('additems.html', item = None, feedback = "Item successfully added!", categories = legit_categories)
            else:
                return render_template('additems.html', item = None, feedback = "Item already exists!", categories = legit_categories)
        else:
            return render_template('additems.html', item = None, feedback = '', categories = legit_categories)
    else:
        return redirect('/')

@app.route('/increase_quantity', methods = ["POST", "GET"])
def increase_quantity():
    if request.method == "POST":
        name = request.form.get('Plus')
        local_account = session['student']
        item = db.session.query(Temporary_Table).filter_by(acc = session['student'], name = name).first()
        item.quantity +=1
        db.session.commit()
        return redirect('/checkout')
    else:
        return "Error encountered. Please login again."

@app.route('/decrease_quantity', methods = ["POST", "GET"])
def decrease_quantity():
    if request.method == "POST":
        if request.form['decremove'] == 'decrease':
            name = request.form.get('Minus')
            local_account = session['student']
            item = db.session.query(Temporary_Table).filter_by(acc = session['student'], name = name).first()
            if item.quantity == 1:
                pass
            else:
                item.quantity -=1
                db.session.commit()
        elif request.form['decremove'] == 'remove':
            name = request.form.get('Minus')
            local_account = session['student']
            Temporary_Table.query.filter_by(acc = local_account, name=name).delete()
            db.session.commit()
        return redirect('/checkout')
    else:
        return "Error encountered. Please login again."

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if "student" in session:
        items = db.session.query(Temporary_Table).filter_by(acc = session['student'])
        all_items = db.session.query(Temporary_Table).filter_by(acc = session['student'])
        total = 0
        for item in all_items:
            if item.promo_price == '-' or item.promo_price == None:
                total += item.quantity * item.price
            else:
                total += item.quantity * item.promo_price

        return render_template('checkout.html',items = items, total = total)
    else:
        return render_template('login.html')

@app.route('/AdminDelete/<int:id>')
def admin_delete(id):
    to_be_deleted = StdAcc.query.get_or_404(id)
    try:
        db.session.delete(to_be_deleted)
        db.session.commit()
    except:
        return "There was a problem deleting that task."

@app.route('/deleteItem/<id>', methods = ['POST', 'GET'])
def delete_item(id):
    if 'admin' in session:
        item = Record_Of_Items.query.get_or_404(id)
        if request.method == "POST":
            if item == None:
                return "Item doesn't exist."
            else:
                os.remove("static/uploads/" + item.image)
                Record_Of_Items.query.filter_by(id = id).delete()
                try:
                    db.session.commit()
                    return redirect('/marketplace')
                except:
                    return 'There was an issue updating your task.'
        else:
            return redirect('/marketplace')
    else:
        return redirect('/login')
        

@app.route('/deleteEntry' , methods = ['POST','GET'])
def deleteEntry():
    if request.method == 'POST':
        if request.form['todo'] == 'Delete':
            acc_user = request.form['usertype']
            acc_name = request.form['username']
            acc_pword = request.form['password']
            if acc_user == 'AdminUser':
                try:
                    check1 = Admin.query.filter_by(name=acc_name, pword=acc_pword).delete()
                    db.session.commit()
                    return "success AdminAcc deletion"
                except:
                    return 'No such User'
            elif acc_user == 'TeacherUser':
                try:
                    check1 = TrAcc.query.filter_by(name=acc_name, pword=acc_pword).delete()
                    db.session.commit()
                    return redirect('/tableteacher')
                except:
                    return 'No such User'
            else:
                try:
                    check1 = StdAcc.query.filter_by(name=acc_name, pword=acc_pword).delete()
                    db.session.commit()
                    return redirect('/tablestudent')
                except:
                    return 'No such User'
        elif request.form['todo'] == 'View Current Cart':
            username = request.form['username']
            items = db.session.query(Temporary_Table).filter_by(acc = username)
            item_test = db.session.query(Temporary_Table).filter_by(acc = username).first()
            text = ""
            if item_test == None:
                text = "Empty Cart"
            else:
                text = ""
            total = 0
            for item in items:
                total += (item.quantity * item.price)
            if 'admin' in session:
                return render_template('viewstudentcart.html',items = items, username = username, text = text, usertype = 'admin', total = total)
            elif 'teacher' in session:
                return render_template('viewstudentcart.html',items = items, username = username, text = text, usertype = 'teacher', total = total)
        

@app.route('/addtocart', methods=['POST', 'GET'])
def add_to_cart():
    if request.method == "POST":
        name = request.form['Add2Cart']
        local_account = session['student']
        check = db.session.query(Temporary_Table).filter_by(name = name, acc = local_account).first()
        if check:
            item = db.session.query(Temporary_Table).filter_by(acc = session['student'], name = name).first()
            item.quantity +=1
            db.session.commit()
            cat = item.cat
            items = db.session.query(Record_Of_Items).filter_by(cat = cat)
            addedToCart = True
            return render_template('marketplace.html',items = items, addedToCart = addedToCart)
        else:
            item = db.session.query(Record_Of_Items).filter_by(name = name).first()
            add_to_cart_item = Temporary_Table(acc = local_account, name = name, info = item.info, price = item.price, quantity = 1, cat = item.cat, promo_price = item.promo_price)
            db.session.add(add_to_cart_item)
            db.session.commit()
            cat = item.cat
            items = db.session.query(Record_Of_Items).filter_by(cat = cat)
            addedToCart = True
            return render_template('marketplace.html',items = items, addedToCart = addedToCart)
    else:
        return "Error encountered. Please login again."

@app.route('/submitcart', methods=["POST", "GET"])
def submit_cart():
    if request.method == "POST":
        local_account = session['student']
        items = db.session.query(Temporary_Table).filter_by(acc = local_account)
        check_for_existing_account = db.session.query(Submitted_Cart).filter_by(acc = local_account).first()
        check_for_existing_items = db.session.query(Temporary_Table).filter_by(acc = local_account).first()
        if check_for_existing_account:
            return render_template('checkout.html', items = items, feedback = "You have already submitted once.", total = 0)
        elif check_for_existing_items == None:
            return render_template('checkout.html', feedback = "There are currently no items in the cart.", total = 0)
        else:
            for item in items:
                new_stuff = Submitted_Cart(acc = local_account, name = item.name, info = item.info, price = item.price, quantity = 1, cat = item.cat)
                db.session.add(new_stuff)
                db.session.commit()
            session.pop('student', None)
            return render_template('success.html')
    else:
        return redirect('/checkout')

@app.route('/success', methods = ['POST', 'GET'])
def success():
    if request.method == 'POST':
        if request.form['todo'] == 'marketplace':
            return redirect('/marketplace')
        elif request.form['todo'] == 'logout':
            return redirect('/logout')
    else:
        return redirect('/login')

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    if "admin" in session:
        session.pop('admin', None)
    elif "teacher" in session:
        session.pop('teacher', None)
    elif "student" in session:
        session.pop('student', None)

    session.clear()
    return redirect('/login')


#MENU(TEACHER AND ADMIN)
@app.route('/admin', methods = ['POST', 'GET'])
def admin():
    if 'admin' in session:
        if request.method == 'POST':
            if request.form['nav'] == 'Table of Teams':
                return redirect('/tablestudent')
            elif request.form['nav'] == 'Table of Teachers':
                return redirect('/tableteacher')
            elif request.form['nav'] == 'Edit Shopping Items':
                return redirect('/marketplace')
            elif request.form['nav'] == 'Reset Options':
                return redirect('/wipedb')
            elif request.form['nav'] == 'Clear Everything':
                return redirect('/reinitialisedb')
            elif request.form['nav'] == 'Create Promotion':
                return redirect('/promotion/Rice')
            elif request.form['nav'] == 'View Promotion':
                displayItem = []
                items = db.session.query(Record_Of_Items).all()
                for item in items:
                    if item.promo_price != '-' and item.promo_price != None:
                        displayItem.append(item)
                return render_template('viewpromotion.html', items = displayItem)
           
            elif request.form['nav'] == 'Reset Promotion':
                items = db.session.query(Record_Of_Items).all()
                for item in items:
                    item.promo_price = None
                db.session.commit()
                session['reset_promo'] = True
                return redirect('/admin')

            elif request.form['nav'] == 'Wipe DB':
                pass
            elif request.form['nav'] == 'Reinitialise DB':
                pass
            elif request.form['nav'] == 'Log Out':
                return redirect('/logout')
        else:
            
            items = db.session.query(Record_Of_Items).all()
            promoReset = False
            msg = None
            if 'published_promo' in session:
                msg = 'PromoPub'
                session.pop('published_promo', None)
            elif 'reset_promo' in session:
                msg = 'PromoRes'
                session.pop('reset_promo', None)
            for item in items:
                if (item.promo_price != '-') and (item.promo_price != None):
                    promoReset = True
                    break
            
            return render_template('admin.html', promoReset = promoReset, msg = msg)

    else:
        return render_template('login.html')


    
@app.route('/teacher', methods = ["POST", 'GET'])
def teacher():
    if 'teacher' in session:
        if request.method == 'POST':
            if request.form['nav'] == 'Table of Student':
                return redirect('/tablestudent')
            elif request.form['nav'] == 'List of Submitted Carts':
                return redirect('/viewsubmittedcarts')
            elif request.form['nav'] == 'Passcodes':
                return redirect('/passcodepage')
            elif request.form['nav'] == 'List of Shopping Items':
                return redirect('/marketplace')
            elif request.form['nav'] == 'Log Out':
                return redirect('/logout')
        else:
            return render_template('teacher.html')
    else:
        return render_template('login.html')

#PAGES

@app.route('/passcodepage', methods = ['POST', 'GET'])
def passcodepage():
    if 'teacher' in session:
        local_account = session['teacher']
        teacher_passcode = db.session.query(TrAcc).filter_by(name = local_account).first().passcode
        return render_template('passcodepage.html', passcode = teacher_passcode)
    else:
        return redirect('/')

@app.route('/wipedbpage', methods = ['POST', 'GET'])
def wipedbpage():
    if 'admin' in session:
        return render_template('wipedbpage.html')
    else:
        return redirect('/login')


@app.route('/changeimage/<imageid>', methods=['POST', 'GET'])
def change_image(imageid):
    if 'admin' in session:
        if request.method == 'POST':
            id = imageid
            changed_image = request.files['changedimage']
            item = db.session.query(Record_Of_Items).filter_by(id=id).first()
            if changed_image and allowed_file(changed_image.filename):
                filename = secure_filename(changed_image.filename)
                changed_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                filename = None
            item.image = filename
            db.session.commit()
            return redirect('/marketplace')
        else:
            return render_template('changeimage.html', imageid = imageid)
    else:
        return redirect('/login')
                   

@app.route('/', methods = ["POST", "GET"])
def redirect_to_login():
    if request.method == "POST":
        if request.form['manipulate'] == 'Edit':
            id = request.form['itemid']
            item = db.session.query(Record_Of_Items).filter_by(id=id).first()
            return render_template('edititems.html', item = item)
        elif request.form['manipulate'] == 'Delete':
            id = request.form['itemid']
            return redirect(url_for('delete_item', id = id), code=307)
        elif request.form['manipulate'] == 'Change Image':
            id = request.form['itemid']
            return redirect(url_for('change_image', imageid = id))
    else:
        return redirect('/login')

@app.route('/authenticate', methods=['POST', 'GET'])
def authenticate():
    if request.method == 'POST':
        passcode = request.form['passcode']
        check_passcode = db.session.query(TrAcc).filter_by(passcode = passcode).first()
        total = 0
        for i in passcode:
            total +=1
        if (check_passcode == None) or (total != 6):
            return render_template('authentication.html', feedback = 'Please key in the correct code.')
        else:
            return redirect('/marketplace')
    else:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def loginpage():
    if request.method == "POST":
        session.pop('admin', None)
        session.pop('teacher', None)
        session.pop('student', None)
        username = request.form['username']
        password = request.form['password']
        check = Admin.query.filter_by(name=username).first()
        if check == None:
            check1 = TrAcc.query.filter_by(name=username).first()
            if check1 == None:
                check2 = StdAcc.query.filter_by(name=username).first()
                if check2 == None:
                    return render_template('login.html', feedback = "No such account exists in records.")
                else:
                    check2 = StdAcc.query.filter_by(name=username, pword = password).first()
                    if check2 == None:
                        return render_template('login.html', feedback = 'Please key in the correct username/password.')
                    else:
                        session['student'] = username
                        return render_template('authentication.html')
            else:
                check1 = TrAcc.query.filter_by(name=username, pword = password).first()
                if check1 == None:
                    return render_template('login.html', feedback = 'Please key in the correct username/password.')
                else:
                    session['teacher'] = username
                    return redirect('/teacher')
        else:
            check = Admin.query.filter_by(name=username, pword = password).first()
            if check == None:
                return render_template('login.html', feedback = 'Please key in the correct username/password.')
            else:
                session['admin'] = username
                return redirect('/admin')
    else:
        return render_template('login.html')


@app.route('/marketplace',methods=['GET','POST'])
def shop_cat():
    if ("student" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Rice':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Breads':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Breads')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Eggs':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Eggs')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Fruits':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fruits')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Fish':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fish')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Paper':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Paper')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Baking':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Baking')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
            return render_template('marketplace.html',items = cat)

    elif ("teacher" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Rice':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Breads':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Breads')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Eggs':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Eggs')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Fruits':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fruits')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Fish':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fish')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Paper':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Paper')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Baking':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Baking')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
            return render_template('protectedmarketplace.html',items = cat)

    elif ("admin" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Rice':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Breads':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Breads')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Eggs':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Eggs')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Fruits':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fruits')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Fish':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fish')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Paper':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Paper')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Baking':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Baking')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Home':
                return redirect('/admin')
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
            return render_template('editpage.html',items = cat)

    else:
        return render_template('login.html')


@app.route('/viewsubmittedcarts', methods = ['post', 'get'])
def view_submitted_carts():
    if 'teacher' in session:
        local_account = session['teacher']
        local_teacher = db.session.query(TrAcc).filter_by(name = local_account).first()
        students = db.session.query(StdAcc).filter_by(assigned_teacher_id = local_teacher.id).all()
        data = db.session.query(Submitted_Cart).all()
        existing_students = []
        for row in data:
            existing_students.append(row.acc)
        set_existing_students = set(existing_students)
        all_total_amounts = []
        for student in students:
            student_items = db.session.query(Submitted_Cart).filter_by(acc = student.name)
            total_price = 0
            for item in student_items:
                total_price += item.price * item.quantity
            all_total_amounts.append(total_price)
        return render_template('testviewstudent.html', students = students, data = data, set_existing_students = set_existing_students, all_total_amounts = all_total_amounts)

@app.route('/tableteacher', methods = ["POST", 'GET'])
def tableTeacher():
    if ("admin" in session):
        listOfTeachers = db.session.query(TrAcc).all()
        return render_template('tableteacher.html',Teachers = listOfTeachers)

    else:
        pass



@app.route('/tablestudent', methods = ["POST", 'GET'])
def tableStudent():
    if "admin" in session:
        students = db.session.query(StdAcc).order_by(db.text('assigned_teacher_id')).all()
        teachers = db.session.query(TrAcc).all()
        usertype = "admin"
        return render_template('tablestudents.html',students = students, teachers = teachers,usertype = usertype)
    
    elif "teacher" in session:
        teacher = db.session.query(TrAcc).filter_by(name = session['teacher']).first()
        students = db.session.query(StdAcc).filter_by(assigned_teacher_id = teacher.id)
        usertype = "teacher"
        return render_template('tablestudents.html',students = students,usertype = usertype)


@app.route('/addTeacher', methods = ['POST', 'GET'])
def addTeacher():
    if request.method == "POST":
        if ('admin' in session):
            usertype = 'admin'
            return render_template('addteachers.html', usertype=usertype)
        else:
            pass
    else:
        pass

@app.route('/addStudent', methods=['POST', 'GET'])
def add_student():
    if request.method == "POST":
        teachers = db.session.query(TrAcc)
        if 'admin' in session:
            usertype = 'admin'
            return render_template('addstudents.html', teachers = teachers, usertype=usertype)
        elif 'teacher' in session:
            usertype = 'teacher'
            return render_template('addstudents.html', teachers = teachers, usertype=usertype)
    else:
        pass


@app.route('/promotion/<category>', methods=['POST', 'GET'])
def promotion(category):
    if 'admin' in session:
        if request.method == 'GET':
            addedPromo = False
            if 'addedPromo' in session:
                addedPromo = True
                session.pop('addedPromo', None)
    
            if category == 'Fruits':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fruits')
                return render_template('promotion.html', items = cat, addedPromo = addedPromo)
            elif category == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Paper':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Paper')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Fish':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fish')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Baking':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Baking')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Fish':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fish')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Eggs':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Eggs')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Breads':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Breads')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Rice':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
                return render_template('promotion.html',items = cat, addedPromo = addedPromo)
            elif category == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Rice')
            return render_template('promotion.html',items = cat)

@app.route('/promotionItems', methods=['POST', 'GET'])
def promotionItems():
    if request.method == 'POST':
        if 'promo_items' not in session:
            session['promo_items'] = []
        itemID = request.form.get('promotionItem')
        itemID_list = session['promo_items']
        if itemID not in itemID_list:
            itemID_list.append(itemID)
        session['promo_items'] = itemID_list
        session['addedPromo'] = True
        cat = db.session.query(Record_Of_Items).filter_by(id = itemID).first()
        return redirect(url_for('promotion', category= cat.cat))




@app.route('/addpromotion', methods=['POST', 'GET'])
def addpromotion():
    if 'admin' in session and 'promo_items' in session:
        items = []
        itemID_list = session['promo_items']
        for itemID in itemID_list:
            item = db.session.query(Record_Of_Items).filter_by(id = itemID).first()
            items.append(item)

        return render_template('addpromotion.html', items = items)
    else:
        return redirect(url_for('promotion', category = "Rice"))

@app.route('/removePromoItem/<item>', methods=['POST', 'GET'])
def removePromoItem(item):
    itemID_list = session['promo_items']
    itemID_list.pop(itemID_list.index(item))
    session['promo_item'] = itemID_list
    return redirect('/addpromotion')




@app.route('/publishpromotion', methods=['POST', 'GET'])
def publishpromotion():
    if request.method == 'POST':
        itemID_list = session['promo_items']
        for idx in itemID_list:
            promo_price = request.form.get(("item" + idx))
            item = db.session.query(Record_Of_Items).filter_by(id = int(idx)).first()
            item.promo_price = promo_price
        db.session.commit()
        flash('New Promotion')
        session['published_promo'] = True
        return redirect('/admin')
    else:
        pass


@app.route('/promoNoti', methods=['POST', 'GET'])
def promoNoti():
    req = request.get_json()
    items = db.session.query(Record_Of_Items).filter(Record_Of_Items.promo_price.isnot(None)).count()
    if 'promoSent' not in session:
        if items > 0:
            res = make_response(jsonify({"message":"promoTrue"}), 200)
            session['promoSent'] = True
        else:
            res = make_response(jsonify({"message":"promoFalse"}), 200)
    else:
        res = make_response(jsonify({"message":"promoSeen"}), 200)
    return res

app.run(host='0.0.0.0', port=8080)