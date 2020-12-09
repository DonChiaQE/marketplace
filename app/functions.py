from flask import Flask, render_template, url_for, request, redirect, flash
import sqlalchemy
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

def shop_cat(category):
    if request.method == 'POST':
        if request.form['navbar'] == cat:
            result = db.session.query(Record_Of_Items).filter_by(cat = result)
            return render_template('marketplace.html',items = result)
        elif request.form['navbar'] == 'Dairy':
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Dairy')
            if cat == None:
                pass
            else:
                return render_template('marketplace.html',items = cat)
        elif request.form['navbar'] == 'Meat':
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Meat')
            return render_template('marketplace.html',items = cat)
        elif request.form['navbar'] == 'Others':
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Other')
            if cat.count() == 0:
                return redirect(url_for('marketplace'))
            else:
                return render_template('marketplace.html',items = cat)
        elif request.form['navbar'] == 'Log Out':
            cat = db.session.query(Record_Of_Items).filter_by(cat = 'Log Out')
            return render_template('marketplace.html',items = cat)
    else:
        Rec = db.session.query(Record_Of_Items).all()
        return render_template('marketplace.html',items = Rec)