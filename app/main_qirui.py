from flask import Flask, render_template, url_for, request, redirect, flash
import sqlalchemy
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Record_Of_Items(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(200),default = '-')
    info = db.Column(db.String(200),default = '-')
    price = db.Column(db.Integer,default = '-')
    cat = db.Column(db.String(200),default = '-')
    image = db.Column(db.String(200),default = '-')


@app.route('/marketplace',methods=['GET','POST'])
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


if __name__ == "__main__":
    app.run(debug=True)
    




