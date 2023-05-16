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
            incoming_orders = db.session.execute(text(f"SELECT * FROM Orders ORDER BY order_date;"))
            recently_added_products = db.session.execute(text(
                f"SELECT *, Products.title FROM Vendor_Products JOIN Products USING(product_id) ORDER BY date_created LIMIT 3;"))
            complaints = db.session.execute(text(
                f"SELECT *, Users.name as author FROM Complaints JOIN Users USING(user_id) ORDER BY complaint_date;"))

            return render_template("admin-home.html", incoming_orders=incoming_orders,
                                   recently_added_products=recently_added_products, complaints=complaints)
        case "VENDOR":
            vendor = Vendor.query.filter_by(
                user_id=current_user.user_id).first()

            vendor_products = VendorProduct.query.filter_by(
                vendor_id=vendor.vendor_id).all()

            incoming_orders = OrderItem.query.filter(
                db.OrderItem.vendor_product.vendor_id == vendor.vendor_id)

            return render_template("vendor_home.html", vendor_products=vendor_products, incoming_orders=incoming_orders)
        case "CUSTOMER":
            customer_id = db.session.execute(
                text(f"SELECT customer_id FROM Customers WHERE user_id = {current_user.user_id}")).first()[0]
            cart_items = db.session.execute(text(
                f"SELECT *, Cart_Items.qty as cart_items_qty FROM Cart_Items JOIN Carts USING(cart_id) JOIN Vendor_Products USING(vendor_product_id) JOIN Products USING(product_id) WHERE customer_id={customer_id}"))
            cart_total = 0

            customer = Customer.query.filter_by(
                user_id=current_user.user_id).first()

            orders = Order.query.filter_by(
                customer_id=customer.customer_id).order_by(Order.order_date).all()

            return render_template("customer_home.html", orders=orders, cart_items=cart_items, cart_total=cart_total)
        case _:
            print("ERROR ROUTING TO HOME")
            return "ERROR ROUTING TO HOME"


@views.route("/shop")
@login_required
def shop():
    categories = [category[0].capitalize() for category in
                  db.session.execute(text(f"SELECT category FROM Products")).all()]

    search = request.args.get("search")
    if search:
        products = db.session.execute(text(
            f"SELECT product_id, title, product_image FROM Products WHERE title LIKE '%{search}%' OR description LIKE '%{search}%'"))
    else:
        category = request.args.get("category")

        if category and category != "all":
            products = db.session.execute(
                text(f"SELECT product_id, title, product_image FROM Products WHERE category='{category}'"))
        else:
            products = db.session.execute(text(f"SELECT product_id, title, product_image FROM Products"))

    categories.insert(0, "All")

    return render_template("shop.html", categories=categories, products=products, search=search)


@views.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@views.route("/shop/product/<int:product_id>")
def products_page(product_id):
    vendor_id = request.args.get("vendor_id")

    product = db.session.execute(
        text(f"select title, description, product_image from Products where product_id={product_id}")).first()
    title = product[0]
    description = product[1]
    product_image = product[2]

    vendors = db.session.execute(text(
        f"select name, vendor_id from Users join Vendors using (user_id) where user_id in (select user_id from Vendors where vendor_id in (select vendor_id from Vendor_Products where product_id = {product_id}))")).all()

    if not vendor_id:
        vendor_id = vendors[0][1]

    colors = db.session.execute(text(
        f"SELECT color FROM Vendor_Product_Colors WHERE vendor_product_id=(SELECT vendor_product_id FROM Vendor_Products WHERE vendor_id={vendor_id} AND product_id={product_id})")).all()
    sizes = db.session.execute(text(
        f"SELECT size FROM Vendor_Product_Sizes WHERE vendor_product_id=(SELECT vendor_product_id FROM Vendor_Products WHERE vendor_id={vendor_id} AND product_id={product_id})")).all()

    colors = [color[0] for color in colors]
    sizes = [size[0] for size in sizes]

    vendor_product_id = db.session.execute(text(
        f"SELECT vendor_product_id FROM Vendor_Products WHERE vendor_id={vendor_id} AND product_id={product_id}")).first()[
        0]
    price = db.session.execute(
        text(f"SELECT price FROM Vendor_Products WHERE vendor_product_id={vendor_product_id}")).first()

    reviews = db.session.execute(text(
        f"SELECT * FROM Reviews JOIN Users USING(user_id) JOIN Vendor_Products USING(vendor_product_id) JOIN Products USING(product_id) WHERE product_id={product_id}")).all()

    return render_template("product_page.html", title=title, description=description, product_image=product_image,
                           vendors=vendors, default_vendor=vendor_id, colors=colors, sizes=sizes, price=price,
                           vendor_product_id=vendor_product_id, reviews=reviews)


@views.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    customer = db.session.execute(text(f"SELECT * FROM Customers WHERE user_id={current_user.user_id}")).first()
    cart = db.session.execute(text(f"SELECT * FROM Carts WHERE customer_id={customer.customer_id}")).first()
    cart_items = db.session.execute(text(
        f"SELECT *, Cart_Items.qty AS item_qty FROM Cart_Items JOIN Vendor_Products USING(vendor_product_id) JOIN Products USING(product_id) WHERE cart_id={cart.cart_id}")).all()
    cart_total = 0
    for cart_item in cart_items.copy():
        vendor_product_id = cart_item.vendor_product_id
        product_price = db.session.execute(
            text(f"SELECT price FROM Vendor_Products WHERE vendor_product_id={vendor_product_id}")).first()
        cart_total += product_price.price * cart_item.item_qty

    if request.method == "POST":
        db.session.execute(
            text(f"INSERT INTO Orders (customer_id, cart_id) VALUES ({customer.customer_id}, {cart.cart_id});"))
        db.session.commit()
        order = db.session.execute(text(f"SELECT * FROM Orders WHERE order_id=LAST_INSERT_ID()")).first()
        for cart_item in cart_items.copy():
            db.session.execute(text(
                f"INSERT INTO Order_Items (order_id, vendor_product_id, qty, color, size) VALUES ({order.order_id}, {cart_item.vendor_product_id}, {cart_item.item_qty}, '{cart_item.color}', '{cart_item.size}');"))
            db.session.commit()
        db.session.execute(text(f"DELETE FROM Cart_Items WHeRE cart_id={cart.cart_id}"))
        db.session.commit()
        return redirect(url_for("views.home"))
    else:
        return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total)


@views.route("/add-to-cart", methods=["POST"])
@login_required
def add_to_cart():
    vendor_product_id = request.form.get("vendor_product_id")
    quantity = request.form.get("quantity")
    color = request.form.get("color")
    size = request.form.get("size")

    customer_id = \
    db.session.execute(text(f"SELECT customer_id FROM Customers WHERE user_id={current_user.user_id}")).first()[0]
    cart_id = db.session.execute(text(f"SELECT cart_id FROM Carts WHERE customer_id={customer_id}")).first()
    if cart_id == None:
        db.session.execute(text(f"INSERT INTO Carts (customer_id) VALUES ({customer_id})"))
        db.session.commit()
        cart_id = db.session.execute(text(f"SELECT cart_id FROM Carts WHERE customer_id={customer_id}")).first()[0]
    else:
        cart_id = cart_id[0]

    db.session.execute(text(
        f"INSERT INTO Cart_Items (cart_id, vendor_product_id, qty, color, size) VALUES ({cart_id}, {vendor_product_id}, {quantity}, '{color}', '{size}')"))
    db.session.commit()
    flash("Successfully added to cart")
    return redirect(url_for("views.shop"))


@views.route("/remove-from-cart", methods=["POST"])
@login_required
def remove_from_cart():
    cart_item_id = request.form.get("cart_item_id")

    db.session.execute(text(f"DELETE FROM Cart_Items WHERE cart_item_id={cart_item_id}"))
    db.session.commit()

    return redirect(request.referrer)