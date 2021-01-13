from flask import Flask, render_template, url_for, request, redirect, flash, session, make_response, jsonify
import sqlalchemy
from sqlalchemy.orm import relationship, load_only
from sqlalchemy.sql import exists
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
    __tablename__ = 'tr_acc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')
    passcode = db.Column(db.String(6), default = '')
    promo_state = db.Column(db.Integer,default = '-')
    assigned_students = db.relationship('StdAcc', backref="assigned_teacher")

class StdAcc(db.Model):
    __tablename__ = 'std_acc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')
    totalamount = db.Column(db.Integer)
    assigned_teacher_id = db.Column(db.Integer, db.ForeignKey('tr_acc.id'))
    totalamount = db.Column(db.Integer, default = 0)
    cart = db.relationship('Cart_Items', backref="student")

class Record_Of_Items(db.Model):
    __tablename__ = 'record_of_items'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    cat = db.Column(db.String(200),default = '-')
    image = db.Column(db.String(200),default = '')
    quantifier = db.Column(db.String(200),default='')
    promo_items = db.relationship('Promo_Items', backref="item")
    cart_items = db.relationship('Cart_Items', backref="item")

class Promo_Items(db.Model):
    __tablename__ = 'promo_items'
    id = db.Column(db.Integer, primary_key=True)
    itemID = db.Column(db.Integer, db.ForeignKey('record_of_items.id'))
    promo_no = db.Column(db.Integer,default = '-')
    promo_price = db.Column(db.Integer,default = '-')

class Cart_Items(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer,primary_key = True)
    acc_id = db.Column(db.Integer, db.ForeignKey('std_acc.id'))
    itemID = db.Column(db.Integer, db.ForeignKey('record_of_items.id'))
    quantity = db.Column(db.Integer,default = '-')

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
            if item.quantifier[:3] == 'for':
                quanextend = request.form['quanextend']
                item.quantifier = item.quantifier + " " + quanextend
            else:
                pass
            try:
                db.session.commit()
                return redirect('/marketplace')
            except:
                return 'There was an issue updating your task.'
        else:
            all_items_categories = db.session.query(Record_Of_Items)
            categories = []
            for cate in all_items_categories:
                categories.append(cate.cat)
            categories.sort()
            legit_categories = set(categories)
            return render_template("edititems.html", item = item, categories = legit_categories)
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
                    db.session.query(Cart_Items).delete()
                    db.session.commit()
                    return redirect('/wipedbpage')
                elif request.form['objectss'] == 'resetpromotion':
                    db.session.query(Promo_Items).delete()
                    teachers = db.session.query(TrAcc).all()
                    for teacher in teachers:
                        teacher.promo_state = None
                    db.session.commit()
                    session['reset_promo'] = True
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
                    db.session.query(Cart_Items).delete()
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
        db.session.query(Cart_Items).delete()
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
        categories.sort()
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
                if new_item_quantifier == 'for':
                    new_item_quanextend = request.form['quanextend']
                    new_item_quantifier = new_item_quantifier + " " + new_item_quanextend
                else:
                    pass
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
        idx = request.form.get('Plus')
        student = db.session.query(StdAcc).filter_by(name = session['student']).first()
        item = db.session.query(Cart_Items).filter_by(itemID = idx, acc_id = student.id).first()
        item.quantity +=1
        db.session.commit()
        return redirect('/checkout')
        
    else:
        return "Error encountered. Please login again."

@app.route('/decrease_quantity', methods = ["POST", "GET"])
def decrease_quantity():
    if request.method == "POST":
        if request.form['decremove'] == 'decrease':
            idx = request.form.get('Minus')
            student = db.session.query(StdAcc).filter_by(name = session['student']).first()
            item = db.session.query(Cart_Items).filter_by(itemID = idx, acc_id = student.id).first()
            if item.quantity == 1:
                pass
            else:
                item.quantity -=1
                db.session.commit()
        elif request.form['decremove'] == 'remove':
            idx = request.form.get('Minus')
            student = db.session.query(StdAcc).filter_by(name = session['student']).first()
            Cart_Items.query.filter_by(acc_id = student.id , itemID = idx).delete()
            db.session.commit()
        return redirect('/checkout')
    else:
        return "Error encountered. Please login again."

@app.route('/removesubmittedcart', methods = ['POST', 'GET'])
def removesubmittedcart():
    if "teacher" in session:
        name = request.form['username']
        db.session.query(Submitted_Cart).filter_by(acc = name).delete()
        db.session.commit()
        return redirect('/viewsubmittedcarts')

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if "student" in session:
        student = db.session.query(StdAcc).filter_by(name = session['student']).first()
        teacher = db.session.query(TrAcc).filter_by(id = student.assigned_teacher_id).first()
        items_promo = db.session.query(Record_Of_Items, Cart_Items, Promo_Items)\
            .filter(Record_Of_Items.id == Cart_Items.itemID)\
            .filter(Promo_Items.itemID == Record_Of_Items.id)\
            .filter(Promo_Items.promo_no == teacher.promo_state)\
            .filter(Cart_Items.acc_id == student.id).order_by(Cart_Items.id).all()
        
        try:
            items = db.session.query(Record_Of_Items, Cart_Items)\
                .filter(Record_Of_Items.id == Cart_Items.itemID)\
                .filter(Record_Of_Items.id.notin_([j.id for j in items_promo[0]]))\
                .filter(Cart_Items.acc_id == student.id).order_by(Cart_Items.id).all()

        except:
            items = db.session.query(Record_Of_Items, Cart_Items)\
                .filter(Record_Of_Items.id == Cart_Items.itemID)\
                .filter(Cart_Items.acc_id == student.id).order_by(Cart_Items.id).all()
        
        total = 0
        for item in items_promo:
            total += item[1].quantity * item[2].promo_price

        for item in items:
            total += item[1].quantity * item[0].price
        items_promomo = filterAllCat()
        return render_template('checkout.html',items = items, items_promo = items_promo, total = total, items_promomo = items_promomo)
    else:
        return render_template('login.html')

@app.route('/promodelete/<promoid>')
def promodelete(promoid):
    to_be_deleted = db.session.query(Promo_Items).filter_by(promo_no = promoid).delete()
    teachers = db.session.query(TrAcc).filter_by(promo_state = promoid).all()
    if teachers:
        for teacher in teachers:
            teacher.promo_state = None
    db.session.commit()
    return redirect('/viewpromotion')

@app.route('/deleteItem/<id>', methods = ['POST', 'GET'])
def delete_item(id):
    if 'admin' in session:
        item = Record_Of_Items.query.get_or_404(id)
        if request.method == "POST":
            if item == None:
                return "Item doesn't exist."
            else:
                if item.image:
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
            userid = request.form['userid']
            items = db.session.query(Cart_Items).filter_by(acc_id = userid)

            student = db.session.query(StdAcc).filter_by(name = username).first()
            check_for_existing_items = db.session.query(Cart_Items).filter_by(acc_id = student.id).first()
            teacher = db.session.query(TrAcc).filter_by(id = student.assigned_teacher_id).first()
            items_promo = db.session.query(Record_Of_Items,Promo_Items, Cart_Items)\
                .filter(Record_Of_Items.id == Cart_Items.itemID)\
                .filter(Promo_Items.itemID == Record_Of_Items.id)\
                .filter(Promo_Items.promo_no == teacher.promo_state)\
                .filter(Cart_Items.acc_id == student.id).all()
            
            try:
                items = db.session.query(Record_Of_Items, Cart_Items)\
                    .filter(Record_Of_Items.id == Cart_Items.itemID)\
                    .filter(Record_Of_Items.id.notin_([j.id for j in items_promo[0]]))\
                    .filter(Cart_Items.acc_id == student.id).all()

            except:
                items = db.session.query(Record_Of_Items, Cart_Items)\
                    .filter(Record_Of_Items.id == Cart_Items.itemID)\
                    .filter(Cart_Items.acc_id == student.id).all()
            
            total = 0
            for item in items_promo:
                total += item[2].quantity * item[1].promo_price

            for item in items:
                total += item[1].quantity * item[0].price

            text = ""
            if check_for_existing_items == None:
                text = "Empty Cart"
            else:
                text = ""
            if 'admin' in session:
                return render_template('viewstudentcart.html', items = items, items_promo = items_promo, username = username, text = text, usertype = 'admin', total = total, userid = userid)
            elif 'teacher' in session:
                return render_template('viewstudentcart.html', items = items, items_promo = items_promo, username = username, text = text, usertype = 'teacher', total = total, userid = userid)
        

@app.route('/addtocart', methods=['POST', 'GET'])
def add_to_cart():
    if request.method == "POST":
        idx = request.form['Add2Cart']
        itemcat = db.session.query(Record_Of_Items).filter_by(id = idx).first()
        quantity_to_add = int(request.form['quantity'])
        local_account = session['student']
        student = db.session.query(StdAcc).filter_by(name = local_account).first()
        check = db.session.query(Cart_Items).filter_by(itemID = idx, acc_id = student.id).first()
        if check:
            check.quantity += quantity_to_add
            db.session.commit()
            items = filterCat(itemcat.cat)
            addedToCart = True
            return render_template('marketplace.html',items_promo = items[0], items=items[1])
        else:
            add_to_cart_item = Cart_Items(student = student, itemID = idx, quantity = quantity_to_add)
            db.session.add(add_to_cart_item)
            db.session.commit()
            items = filterCat(itemcat.cat)
            addedToCart = True
            return render_template('marketplace.html',items_promo = items[0], items=items[1])
    else:
        return "Error encountered. Please login again."

@app.route('/submitcart', methods=["POST", "GET"])
def submit_cart():
    if request.method == "POST":
        check_for_existing_account = db.session.query(Submitted_Cart).filter_by(acc = session['student']).first()
        gotsubmit = check_for_existing_account
        student = db.session.query(StdAcc).filter_by(name = session['student']).first()
        check_for_existing_items = db.session.query(Cart_Items).filter_by(acc_id = student.id).first()
        teacher = db.session.query(TrAcc).filter_by(id = student.assigned_teacher_id).first()
        items_promo = db.session.query(Record_Of_Items,Promo_Items, Cart_Items).filter(Record_Of_Items.id == Cart_Items.itemID)\
            .filter(Promo_Items.itemID == Record_Of_Items.id)\
            .filter(Promo_Items.promo_no == teacher.promo_state)\
            .filter(Cart_Items.acc_id == student.id).all()
        
        try:
            items = db.session.query(Record_Of_Items, Cart_Items)\
                .filter(Record_Of_Items.id == Cart_Items.itemID)\
                .filter(Record_Of_Items.id.notin_([j.id for j in items_promo[0]]))\
                .filter(Cart_Items.acc_id == student.id).all()

        except:
            items = db.session.query(Record_Of_Items, Cart_Items)\
                .filter(Record_Of_Items.id == Cart_Items.itemID)\
                .filter(Cart_Items.acc_id == student.id).all()
        
        total = 0
        for item in items_promo:
            total += item[2].quantity * item[1].promo_price

        for item in items:
            total += item[1].quantity * item[0].price
        
        if check_for_existing_account:
            gotsubmit = True
            return render_template('checkout.html', items_promo = items_promo, items = items, feedback = "You have already submitted once.", total = total, gotsubmit = gotsubmit)
        elif check_for_existing_items == None:
            gotitems = False
            return render_template('checkout.html', feedback = "There are currently no items in the cart.", total = total, gotitems = gotitems)
        else:
            try:
                for item in items_promo:
                    new_Promo = Submitted_Cart(acc = session['student'], name = item[0].name, info = item[0].info, price = item[0].price, quantity = item[2].quantity, cat = item[0].cat)
                    db.session.add(new_Promo)
                for item in items:
                    new_Items = Submitted_Cart(acc = session['student'], name = item[0].name, info = item[0].info, price = item[0].price, quantity = item[1].quantity, cat = item[0].cat)
                    db.session.add(new_Items)
                db.session.commit()
                
            except:
                for item in items:
                    new_Items = Submitted_Cart(acc = session['student'], name = item[0].name, info = item[0].info, price = item[0].price, quantity = item[1].quantity, cat = item[0].cat)
                    db.session.add(new_Items)
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
            elif request.form['nav'] == 'View Promotion':
                return redirect('/viewpromotion')
            elif request.form['nav'] == 'Log Out':
                return redirect('/logout')
        else:
            '''
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
            '''
            return render_template('admin.html')

    else:
        return render_template('login.html')


    
@app.route('/teacher', methods = ["POST", 'GET'])
def teacher():
    if 'teacher' in session:
        if request.method == 'POST':
            if request.form['nav'] == 'Table of Teams':
                return redirect('/tablestudent')
            elif request.form['nav'] == 'List of Submitted Carts':
                return redirect('/viewsubmittedcarts')
            elif request.form['nav'] == 'Passcodes':
                return redirect('/passcodepage')
            elif request.form['nav'] == 'List of Shopping Items':
                return redirect('/marketplace')
            elif request.form['nav'] == 'Launch Promotion':
                return redirect('/viewpromotion')
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

@app.route('/teacherpromo')
def teacherpromo():
    if 'teacher' in session:
        return render_template('teacherpromo.html')

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
            all_items_categories = db.session.query(Record_Of_Items)
            categories = []
            for cate in all_items_categories:
                categories.append(cate.cat)
            categories.sort()
            legit_categories = set(categories)
            return render_template('edititems.html', item = item, categories = legit_categories)
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
        session.pop('admin', None)
        session.pop('teacher', None)
        session.pop('student', None)
        return render_template('login.html')

def filterCat(cat):
    if 'student' in session:
        student = db.session.query(StdAcc).filter_by(name = session['student']).first()
        teacher = db.session.query(TrAcc).filter_by(id = student.assigned_teacher_id).first()
    else:
        teacher = db.session.query(TrAcc).filter_by(name = session['teacher']).first()

    items_promo = db.session.query(Record_Of_Items,Promo_Items)\
    .filter(Record_Of_Items.id == Promo_Items.itemID)\
    .filter(Promo_Items.promo_no == teacher.promo_state)\
    .filter(Record_Of_Items.cat == cat).all()

    try:
        items = db.session.query(Record_Of_Items).filter(Record_Of_Items.id.notin_([j[1].itemID for j in items_promo]))\
                .filter(Record_Of_Items.cat == cat).all()

    except:
        items = db.session.query(Record_Of_Items)\
                .filter(Record_Of_Items.cat == cat).all()

    return items_promo, items

def filterAllCat():
    if 'student' in session:
        student = db.session.query(StdAcc).filter_by(name = session['student']).first()
        teacher = db.session.query(TrAcc).filter_by(id = student.assigned_teacher_id).first()
    else:
        teacher = db.session.query(TrAcc).filter_by(name = session['teacher']).first()

    items_promo = db.session.query(Record_Of_Items,Promo_Items)\
    .filter(Record_Of_Items.id == Promo_Items.itemID)\
    .filter(Promo_Items.promo_no == teacher.promo_state).all()

    return items_promo

@app.route('/marketplace',methods=['GET','POST'])
def shop_cat():
    if ("student" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Rice':
                items = filterCat('Rice')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Dairy':
                items = filterCat('Dairy')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Breads':
                items = filterCat('Breads')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Eggs':
                items = filterCat('Eggs')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Fruits':
                items = filterCat('Fruits')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Fish':
                items = filterCat('Fish')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Paper':
                items = filterCat('Paper')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Baking':
                items = filterCat('Baking')
                items_promomo = filterAllCat()
                return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            items_promomo = filterAllCat()
            items = filterCat('Rice')
            return render_template('marketplace.html',items_promo = items[0], items=items[1], items_promomo = items_promomo)

    elif ("teacher" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Rice':
                items = filterCat('Rice')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Dairy':
                items = filterCat('Dairy')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Breads':
                items = filterCat('Rice')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Eggs':
                items = filterCat('Eggs')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Fruits':
                items = filterCat('Fruits')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Fish':
                items = filterCat('Fish')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Paper':
                items = filterCat('Paper')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Baking':
                items = filterCat('Baking')
                return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            items = filterCat('Rice')
            return render_template('protectedmarketplace.html',items_promo = items[0], items=items[1])

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
            return render_template('editpage.html', items = cat)

    else:
        return render_template('login.html')


@app.route('/viewsubmittedcarts', methods = ['POST', 'GET'])
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
        for student in students:
            student_items = db.session.query(Submitted_Cart).filter_by(acc = student.name)
            total_price = 0
            for item in student_items:
                total_price += item.price * item.quantity
            student.totalamount = total_price
        db.session.commit()
        return render_template('testviewstudent.html', students = students, data = data, set_existing_students = set_existing_students)

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
def promotion(category, promo_no=None):
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
        check_promo = db.session.query(Promo_Items)\
                .filter(Promo_Items.promo_no == session['promo_no']).delete()
        insert_entries = []
        for idx in itemID_list:
            promo_price = request.form.get(("item" + idx))
            insert_entries.append(Promo_Items(itemID = idx, promo_no=session['promo_no'],promo_price=promo_price))
        
        db.session.bulk_save_objects(insert_entries)
        db.session.commit()
        session['promo_items'] = []
        return redirect('/viewpromotion')
    else:
        pass


@app.route('/promoNoti', methods=['POST', 'GET'])
def promoNoti():
    req = request.get_json()
    student = db.session.query(StdAcc).filter_by(name = session['student']).first()
    teacher = db.session.query(TrAcc).filter_by(id = student.assigned_teacher_id).first()
    promo_sent = 'promoSent' + str(teacher.promo_state)

    if promo_sent not in session:
        res = make_response(jsonify({"message":promo_sent}), 200)
        session[promo_sent] = True
    else:
        res = make_response(jsonify({"message":"NoPromo"}), 200)

    return res


@app.route('/viewpromotion', methods=['POST', 'GET'])
def viewpromotion():
        if request.method == 'GET':
            promo_dis1 = db.session.query(Record_Of_Items,Promo_Items)\
                .filter(Promo_Items.promo_no == 1)\
                .filter(Record_Of_Items.id == Promo_Items.itemID)

            promo_dis2 = db.session.query(Record_Of_Items,Promo_Items)\
                .filter(Promo_Items.promo_no == 2)\
                .filter(Record_Of_Items.id == Promo_Items.itemID)

            promo_dis3 = db.session.query(Record_Of_Items,Promo_Items)\
                .filter(Promo_Items.promo_no == 3)\
                .filter(Record_Of_Items.id == Promo_Items.itemID)

            if 'admin' in session:
                return render_template('viewpromotion.html',promo_dis1= promo_dis1,\
                    promo_dis2= promo_dis2, promo_dis3=promo_dis3)
        
            elif 'teacher' in session:
                teacher = db.session.query(TrAcc).filter_by(name = session['teacher']).first()
                return render_template('teacherpromo.html', current_promo = teacher.promo_state, promo_dis1= promo_dis1,\
                    promo_dis2= promo_dis2, promo_dis3=promo_dis3)


@app.route('/setPromoNo/<promo_no>', methods=['POST', 'GET'])
def setPromoNo(promo_no):
    if 'admin' in session:
        if 'promo_no' not in session or session['promo_no'] != promo_no:
            session['promo_no'] = promo_no

        return redirect(url_for('promotion',category='Rice'))

@app.route('/setTeacherPromoState', methods=['POST', 'GET'])
def setTeacherPromoState():
    if 'teacher' in session:
        promoState = request.form.get('promo_state')
        teacher = db.session.query(TrAcc).filter_by(name = session['teacher']).first()
        teacher.promo_state = promoState
        db.session.commit()
        return redirect('/teacher')


@app.route('/test', methods=['POST', 'GET'])
def test():
    student = db.session.query(StdAcc).filter_by(name = session['student']).first()
    teacher = db.session.query(TrAcc).filter_by(id = student.assigned_teacher_id).first()
    items = db.session.query(Cart_Items)\
    .filter_by(acc_id = student.id).order_by(Cart_Items.id).all()
    items_promo = db.session.query(Cart_Items)\
        .filter(Record_Of_Items.id == Cart_Items.itemID)\
        .filter(Promo_Items.itemID == Record_Of_Items.id)\
        .filter(Promo_Items.promo_no == teacher.promo_state)\
        .filter(Cart_Items.acc_id == student.id).order_by(Cart_Items.id).all()
    req = request.get_json()
    #print(req['quantity' + str(items[0].itemID)])
    stuff = req['yo'].splitlines()
    for lol in stuff:
        lol.replace('        ', '')
        print(lol)
    print(stuff)
    return req
    

    
if __name__ == "__main__":
    app.run(debug=True)