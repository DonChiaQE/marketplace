from flask import Flask, render_template, url_for, request, redirect, flash
import sqlalchemy
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # the login view of your application
app.config['SECRET_KEY'] = "lkkajdghdadkglajkgah" # a secret key for your app

class User(UserMixin):
    def __init__(self,id):
        self.id = id

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')

class TrAcc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')

class StdAcc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), default = '-')
    pword = db.Column(db.String(200), default = '-')

class Record_Of_Items(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    cat = db.Column(db.String(200),default = '-')
    image = db.Column(db.String(200),default = '-')

class Temporary_Table(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    acc = db.Column(db.String(200),default = '-')
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    cat = db.Column(db.String(200),default = '-')

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/TrDB', methods=['POST','GET'])
def database():
    new_teacher_acc = TrAcc(name = "Smallus", pword = "Peniusus")
    return "render_template('card.html', acc=new_teacher_acc)"
    

@app.route('/StdDB', methods=['POST','GET'])
def std():
    new_student_acc = StdAcc(name = "Biggus", pword = "Dickus")
    db.session.add(new_student_acc)
    db.session.commit()
    return "render_template('marketplace.html', new=new_teacher_acc)"

@app.route('/login', methods=['POST', 'GET'])
def loginpage():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        check = Admin.query.filter_by(name=username, pword=password).first()
        if check == None:
            check1 = TrAcc.query.filter_by(name=username, pword=password).first()
            if check1 == None:
                check2 = StdAcc.query.filter_by(name=username, pword=password).first()
                if check2 == None:
                    return "No such account exists in records."
                else:
                    local_account = username
                    Rec = db.session.query(Record_Of_Items).all()
                    return render_template('marketplace.html',items = Rec)
            else:
                local_account = username
                Rec = db.session.query(Record_Of_Items).all()
                return render_template('marketplace.html',items = Rec)
        else:
            local_account = username
            Rec = db.session.query(Record_Of_Items).all()
            return render_template('marketplace.html',items = Rec)
    else:
        return render_template('login.html')

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
                return "success AdminAcc creation"
        elif new_acc_user == 'TeacherUser':
            check1 = TrAcc.query.filter_by(name=new_acc_name, pword=new_acc_pword).first()
            if check1 == None:
                new_acc = TrAcc(name = new_acc_name, pword = new_acc_pword)
                db.session.add(new_acc)
                return "success TeacherAcc creation"
        else:
            check2 = StdAcc.query.filter_by(name=new_acc_name, pword=new_acc_pword).first()
            if check2 == None:
                new_acc = StdAcc(name = new_acc_name, pword = new_acc_pword)
                db.session.add(new_acc)
                return "success StudentAcc creation"

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    return render_template('checkout.html')

@app.route('/AdminDelete/<int:id>')
def admin_delete(id):
    to_be_deleted = Admin.query.get_or_404(id)
    try:
        db.session.delete(to_be_deleted)
        db.session.commit()
        #booking= BookDR.query.order_by(BookDR.id).all()
        #return render_template('database.html',booking=booking)
    except:
        return "There was a problem deleting that task."

@app.route('/marketplace',methods=['GET','POST'])
@login_required
def shop_cat():
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
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Log Out')
            return render_template('marketplace.html',items = cat)
        else:
            Rec = db.session.query(Record_Of_Items).all()
            return render_template('marketplace.html',items = Rec)
    else:
        Rec = db.session.query(Record_Of_Items).all()
        return render_template('marketplace.html',items = Rec)

@app.route('/addtocart', methods=['POST', 'GET'])
def add_to_cart():
    if request.method == "POST":
        name = request.form['Add2Cart']
        item = db.session.query(Record_Of_Items).filter_by(name = name).first()
        add_to_cart_item = Temporary_Table( name = name, info = item.info, price = item.price, cat = item.cat)
        db.session.add(add_to_cart_item)
        db.session.commit()
        Rec = db.session.query(Record_Of_Items).all()
        return render_template('marketplace.html',items = Rec)
    else:
        return "error"

if __name__ == "__main__":
    app.run(debug=True)
    




