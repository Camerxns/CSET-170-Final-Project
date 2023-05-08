from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import text, create_engine
from .models import *
from . import db

conn_str = "mysql://root:Brody678@localhost/cset_180_final_project"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template("index.html")

@views.route("/base")        
def base():
    return render_template("base.html")

@views.route("/home")


# @login_required

def home():
    t = conn.execute(text(f"SELECT * from carts join cart_items join products using(product_id) where customer_id = {current_user.user_id};"))
    rows = t.fetchall()
    return render_template("home.html", rows)
    
    match current_user.account_type:
        case "ADMIN":
            admin = Admin.query.filter_by(user_id=current_user.user_id).first()

            products = VendorProduct.query.all()

            incoming_orders = OrderItem.query.all()

            return render_template("vendor_home.html", vendor_products=products, incoming_orders=incoming_orders)
        case "VENDOR":
            vendor = Vendor.query.filter_by(
                user_id=current_user.user_id).first()

            vendor_products = VendorProduct.query.filter_by(
                vendor_id=vendor.vendor_id).all()

            incoming_orders = OrderItem.query.filter(
                db.OrderItem.vendor_product.vendor_id == vendor.vendor_id)

            return render_template("vendor_home.html", vendor_products=vendor_products, incoming_order=incoming_orders)
        case "CUSTOMER":
            customer = Customer.query.filter_by(
                user_id=current_user.user_id).first()

            cart_items = CartItem.query.filter_by(
                db.CartItem.cart.customer_id == customer.customer_id).all()

            orders = Order.query.filter_by(
                customer_id=customer.customer_id).order_by(Order.order_date).all()

            return render_template("customer_home.html", orders=orders, cart_items=cart_items)
        case _:
            print("ERROR ROUTING TO HOME")
            return "ERROR ROUTING TO HOME"




@views.route("/profile")
def profile():
    return render_template("profile.html")
