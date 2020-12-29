from flask import Flask, render_template, url_for, request, redirect, flash
import sqlalchemy
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

def shop_cat(category):
    if request.form['navbar'] == category:
        result = db.session.query(Record_Of_Items).filter_by(cat = category)
        return render_template('marketplace.html',items = result)
        