from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text, create_engine
from .models import *
from . import db

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template("index.html")

@views.route("/base")        
def base():
    return render_template("base.html")

@views.route("/home")

@login_required
def home():    
    match current_user.account_type():
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

            return render_template("vendor_home.html", vendor_products=vendor_products, incoming_orders=incoming_orders)
        case "CUSTOMER":
            result = db.session.execute(text(f"select title, description, product_image, category from Carts natural join Cart_Items join Products using(product_id) where customer_id = { current_user.user_id };")).all()
            customer = Customer.query.filter_by(
                user_id=current_user.user_id).first()

            orders = Order.query.filter_by(
                customer_id=customer.customer_id).order_by(Order.order_date).all()

            return render_template("customer_home.html", orders=orders, cart_items=result)
        case _:
            print("ERROR ROUTING TO HOME")
            return "ERROR ROUTING TO HOME"


@views.route("/shop")
@login_required
def shop():
    categories = [category[0].capitalize() for category in db.session.execute(text(f"SELECT category FROM Products")).all()]

    search = request.args.get("search")
    if search:
        products = db.session.execute(text(f"SELECT product_id, title, product_image FROM Products WHERE title LIKE '%{search}%' OR description LIKE '%{search}%'"))
    else:
        category = request.args.get("category")

    
        categories.insert(0, "All")
    
        if category and category != "all":
            products = db.session.execute(text(f"SELECT product_id, title, product_image FROM Products WHERE category='{category}'"))
        else:
            products = db.session.execute(text(f"SELECT product_id, title, product_image FROM Products"))
    
    return render_template("shop.html", categories=categories, products=products, search=search)


@views.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@views.route("/shop/product/<int:product_id>")
def products_page(product_id):
    vendor_id = request.args.get("vendor_id")
    
    product= db.session.execute(text(f"select title, description, product_image from Products where product_id={product_id}")).first()
    title=product[0]
    description=product[1]
    product_image=product[2]

    vendors = db.session.execute(text(f"select name, vendor_id from Users join Vendors using (user_id) where user_id in (select user_id from Vendors where vendor_id in (select vendor_id from Vendor_Products where product_id = {product_id}))")).all()

    if not vendor_id:
        vendor_id = vendors[0][1]
    
    colors = db.session.execute(text(f"SELECT color FROM Vendor_Product_Colors WHERE vendor_product_id=(SELECT vendor_product_id FROM Vendor_Products WHERE vendor_id={vendor_id} AND product_id={product_id})")).all()
    sizes = db.session.execute(text(f"SELECT size FROM Vendor_Product_Sizes WHERE vendor_product_id=(SELECT vendor_product_id FROM Vendor_Products WHERE vendor_id={vendor_id} AND product_id={product_id})")).all()
    
    colors = [color[0] for color in colors]
    sizes = [size[0] for size in sizes]

    vendor_product_id = db.session.execute(text(f"SELECT vendor_product_id FROM Vendor_Products WHERE vendor_id={vendor_id} AND product_id={product_id}")).first()[0]
    price = db.session.execute(text(f"SELECT price FROM Vendor_Products WHERE vendor_product_id={vendor_product_id}")).first()

    return render_template("product_page.html", title=title, description=description, product_image=product_image, vendors=vendors, default_vendor=vendor_id, colors=colors, sizes=sizes, price=price)
    
   
   
    
@views.route("/checkout")
def checkout():
   # Retrieve cart items from the database
    

    return render_template("checkout.html")

    
@views.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart():
    vendor_product_id = request.form.get("vendor_product_id")
    quantity = request.form.get("quantity")
    color = request.form.get("color")
    size = request.form.get("size")

    customer_id = db.session.execute(text(f"SELECT customer_id FROM Customers WHERE user_id={current_user.user_id}")).first()[0]
    cart_id = db.session.execute(text(f"SELECT cart_id FROM Carts WHERE customer_id={customer_id}")).first()
    if cart_id == None:
        db.session.execute(text(f"INSERT INTO Carts (customer_id) VALUES ({customer_id})"))
        db.session.commit()
        cart_id = db.session.execute(text(f"SELECT cart_id FROM Carts WHERE customer_id={customer_id}")).first()[0]
    else:
        cart_id = cart_id[0]
    
    db.session.execute(text(f"INSERT INTO Cart_Items (cart_id, vendor_product_id, qty, color, size) VALUES ({cart_id}, {vendor_product_id}, {quantity}, '{color}', '{size}')"))
    db.session.commit()
    flash("Successfully added to cart")
    return redirect(url_for("views.shop"))
