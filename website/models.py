from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin


class Users(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)
    admins = db.relationship('Admins', backref='user', uselist=False)
    vendors = db.relationship('Vendors', backref='user', uselist=False)
    customers = db.relationship('Customers', backref='user', uselist=False)


class Admins(db.Model):
    __tablename__ = 'Admins'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), unique=True, nullable=False)
    user = db.relationship('Users', backref='admin')


class Vendors(db.Model):
    __tablename__ = 'Vendors'
    vendor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), unique=True, nullable=False)
    user = db.relationship('Users', backref='vendor')


class Customers(db.Model):
    __tablename__ = 'Customers'
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), unique=True, nullable=False)
    user = db.relationship('Users', backref='customer')


class Products(db.Model):
    __tablename__ = 'Products'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(40), nullable=False)
    description = db.Column(db.Text, nullable=False)
    product_image = db.Column(db.String(255), nullable=False)
    category = db.Column(db.Integer, nullable=False)


class Vendor_Products(db.Model):
    __tablename__ = 'Vendor_Products'
    vendor_product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, nullable=False)
    vendor_id = db.Column(db.Integer, nullable=False)
    qty = db.Column(db.Integer, nullable=False, d)
