from flask import Flask, render_template, url_for, request, redirect, flash, session
import sqlalchemy
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin

app = Flask(__name__)
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "lkkajdghdadkglajkgajdisa931!.h" # a secret key for your app

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')

class TrAcc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')
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
    image = db.Column(db.String(200),default = '-')
    quantifier = db.Column(db.String(200),default=None)

class Temporary_Table(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    acc = db.Column(db.String(200),default = '-')
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    quantity = db.Column(db.Integer,default = 1)
    cat = db.Column(db.String(200),default = '-')

class Submitted_Cart(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    acc = db.Column(db.String(200),default = '-')
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    quantity = db.Column(db.Integer,default = 1)
    cat = db.Column(db.String(200),default = '-')


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

@app.route('/additems', methods=["POST", 'GET'])
def additems():
    if 'admin' in session:
        if request.method == 'POST':
            new_item_name = request.form['itemname']
            new_item_price = request.form['itemprice']
            new_item_info = request.form['iteminfo']
            new_item_cat = request.form['itemcat']
            new_item_quantifier = request.form['itemquantifier']
            check = Record_Of_Items.query.filter_by(name=new_item_name).first()
            if check == None:
                new_item = Record_Of_Items(name = new_item_name, price = new_item_price, info = new_item_info, cat = new_item_cat, quantifier = new_item_quantifier)
                db.session.add(new_item)
                db.session.commit()
                return redirect('/marketplace')
            else:
                return "Item already exists!"
        else:
            return render_template('additems.html', item = None)
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
        name = request.form.get('Minus')
        local_account = session['student']
        item = db.session.query(Temporary_Table).filter_by(acc = session['student'], name = name).first()
        if item.quantity == 1:
            Temporary_Table.query.filter_by(acc = local_account, name=name).delete()
            db.session.commit()
        else:
            item.quantity -=1
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
            total += item.quantity * item.price
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
        acc_user = request.form['usertype']
        acc_name = request.form['username']
        acc_pword = request.form['password']
        if acc_user == 'AdminUser':
            try:
                check1 = TrAcc.query.filter_by(name=acc_name, pword=acc_pword).delete()
                db.session.commit()
                return "success AdminAcc deletion"
            except:
                return 'No such User'
        elif acc_user == 'TeacherUser':
            try:
                check1 = TrAcc.query.filter_by(name=acc_name, pword=acc_pword).delete()
                db.session.commit()
                return "success TeacherAcc deletion"
            except:
                return 'No such User'
        else:
            try:
                check1 = StdAcc.query.filter_by(name=acc_name, pword=acc_pword).delete()
                db.session.commit()
                return "success StudentAcc deletion"
            except:
                return 'No such User'
        

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
            add_to_cart_item = Temporary_Table(acc = local_account, name = name, info = item.info, price = item.price, quantity = 1, cat = item.cat)
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
            return "You have already submitted once."
        elif check_for_existing_items == None:
            return "There are currently no items in the cart."
        else:
            for item in items:
                new_stuff = Submitted_Cart(acc = local_account, name = item.name, info = item.info, price = item.price, quantity = 1, cat = item.cat)
                db.session.add(new_stuff)
                db.session.commit()
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
            return render_template('marketplace.html',items = cat)
    else:
        return redirect('/checkout')

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    if "admin" in session:
        session.pop('admin', None)
    elif "teacher" in session:
        session.pop('teacher', None)
    elif "student" in session:
        session.pop('student', None)

    session.clear()
    return render_template('login.html')


#MENU(TEACHER AND ADMIN)
@app.route('/admin', methods = ['POST', 'GET'])
def admin():
    if 'admin' in session:
        if request.method == 'POST':
            if request.form['nav'] == 'Table of Student':
                return redirect('/tablestudent')
            elif request.form['nav'] == 'Table of Teachers':
                return redirect('/tableteacher')
            elif request.form['nav'] == 'Edit Shopping Items':
                return redirect('/marketplace')
            elif request.form['nav'] == 'Create Promotion':
                return redirect('/promotion')
            elif request.form['nav'] == 'Wipe DB':
                pass
            elif request.form['nav'] == 'Reinitialise DB':
                pass
        else:
            return render_template('admin.html')

    else:
        return render_template('login.html')


    
@app.route('/teacher', methods = ["POST", 'GET'])
def teacher():
    if 'teacher' in session:
        if request.method == 'POST':
            if request.form['nav'] == 'Table of Student':
                return redirect('/tablestudent')
            elif request.form['nav'] == 'List of Shopping Items':
                return redirect('/marketplace')
        else:
            return render_template('teacher.html')
    else:
        return render_template('login.html')


#PAGES

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
                    return "No such account exists in records."
                else:
                    check2 = StdAcc.query.filter_by(name=username, pword = password).first()
                    if check2 == None:
                        return "Please key in your username/password again."
                    else:
                        session['student'] = username
                        cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
                        return render_template('marketplace.html',items = cat)
            else:
                check1 = TrAcc.query.filter_by(name=username, pword = password).first()
                if check1 == None:
                    return "Please key in your username/password again."
                else:
                    session['teacher'] = username
                    return render_template('teacher.html')
        else:
            check = Admin.query.filter_by(name=username, pword = password).first()
            if check == None:
                return "Please key in your username/password again."
            else:
                session['admin'] = username
                return render_template('admin.html')
    else:
        return render_template('login.html')


@app.route('/marketplace',methods=['GET','POST'])
def shop_cat():
    if ("student" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Fresh Produce':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Meat':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Meat')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Others':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Others')
                return render_template('marketplace.html',items = cat)
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
            return render_template('marketplace.html',items = cat)

    elif ("teacher" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Fresh Produce':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Meat':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Meat')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Others':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Others')
                return render_template('protectedmarketplace.html',items = cat)
            elif request.form['navbar'] == 'Home':
                return render_template('teacher.html')
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
            return render_template('protectedmarketplace.html',items = cat)

    elif ("admin" in session):
        if request.method == 'POST':
            if request.form['navbar'] == 'Fresh Produce':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Meat':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Meat')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Others':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Others')
                return render_template('editpage.html',items = cat)
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
            return render_template('editpage.html',items = cat)

    else:
        return render_template('login.html')




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


@app.route('/promotion', methods=['POST', 'GET'])
def promotion():
    if 'admin' in session:
        if request.method == 'POST':
            if request.form['navbar'] == 'Fresh Produce':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
                return render_template('promotion.html',items = cat)
            elif request.form['navbar'] == 'Dairy':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
                return render_template('promotion.html',items = cat)
            elif request.form['navbar'] == 'Meat':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Meat')
                return render_template('promotion.html',items = cat)
            elif request.form['navbar'] == 'Others':
                cat = db.session.query(Record_Of_Items).filter_by(cat = 'Others')
                return render_template('promotion.html',items = cat)
            elif request.form['navbar'] == 'Log Out':
                return redirect('/logout')
        else:
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Fresh Produce')
            return render_template('promotion.html',items = cat)




if __name__ == "__main__":
    app.run(debug=True)
    






