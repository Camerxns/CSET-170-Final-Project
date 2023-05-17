from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import text, create_engine
from werkzeug.utils import secure_filename
from .models import *
from werkzeug.utils import secure_filename, redirect, send_from_directory
from . import db

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template("index.html")


@views.route("/base")
def base():
    return render_template("base.html")

@views.route("/home", methods= ["GET", "POST"])
@login_required
def home():
    match current_user.account_type():
        case "ADMIN":
            incoming_orders = db.session.execute(text(f"SELECT * FROM Orders ORDER BY order_date;"))
            recently_added_products = db.session.execute(text(
                f"SELECT *, Products.title FROM Vendor_Products JOIN Products USING(product_id) ORDER BY date_created LIMIT 3;"))
            complaints = db.session.execute(text(
                f"SELECT *, Users.name as author FROM Complaints JOIN Users USING(user_id) ORDER BY complaint_date;"))
            chats = db.session.execute(text(f"SELECT * FROM Chats"))

            return render_template("admin-home.html", incoming_orders=incoming_orders,
                                   recently_added_products=recently_added_products, complaints=complaints, chats=chats)
        case "VENDOR":
            vendor = Vendor.query.filter_by(
                user_id=current_user.user_id).first()

            vendor_products = VendorProduct.query.filter_by(
                vendor_id=vendor.vendor_id).all()
            categories = [category[0].capitalize() for category in db.session.execute(text(f"SELECT category FROM Products where product_id IN (select product_id from Vendor_Products where vendor_id = (select vendor_id from Vendors where user_id = {current_user.user_id}))")).all()]
            categories.insert(0, "All")
            
            incoming_orders = db.session.execute(text(f"select status, customers.customer_id, order_id, name, title, product_id from orders join customers natural join users natural join products;")).all()
            vendor_product_images = db.session.execute(text(f"select product_image from Products where product_id IN (select product_id from Vendor_Products where vendor_id = (select vendor_id from Vendors where user_id = {current_user.user_id}))")).all()

            if request.method == "POST":
                choices = request.form.get("vendor-options")
                if choices == 'add':
                    return redirect(url_for("views.vendor_add"))
                
                elif choices == 'edit':
                    return redirect(url_for("views.admin_edit"))

                elif choices == 'delete':
                    return redirect(url_for("views.admin_delete"))

            total_orders = []
            shipped_orders = []
            pending_orders = []

            for order in incoming_orders:
                if order[0] == "pending":
                    pending_orders.append(order)
                elif order[0] == "shipped":
                    shipped_orders.append(order)
                total_orders.append(order)

            return render_template("vendor_home.html", categories=categories, vendor_products=vendor_products, vendor_product_images=vendor_product_images, incoming_orders=total_orders, pending_orders=pending_orders, shipped_orders=shipped_orders)
        case "CUSTOMER":
            customer_id = db.session.execute(
                text(f"SELECT customer_id FROM Customers WHERE user_id = {current_user.user_id}")).first()[0]
            cart_items = db.session.execute(text(
                f"SELECT *, Cart_Items.qty as cart_items_qty FROM Cart_Items JOIN Carts USING(cart_id) JOIN Vendor_Products USING(vendor_product_id) JOIN Products USING(product_id) WHERE customer_id={customer_id}"))
            cart_total = 0

            customer = Customer.query.filter_by(
                user_id=current_user.user_id).first()

            pending_orders = db.session.execute(text(f"SELECT * FROM Orders WHERE status=\"pending\""))
            shipped_orders = db.session.execute(text(f"SELECT * FROM Orders WHERE status=\"shipped\""))
            delivered_orders = db.session.execute(text(f"SELECT * FROM Orders WHERE status=\"delivered\""))

            reviews = db.session.execute(text(f"SELECT Products.title AS product_title, Products.product_id AS product_id, Reviews.* FROM Reviews JOIN Products USING(product_id) ORDER BY review_date LIMIT 3"))

            return render_template("customer_home.html", pending_orders=pending_orders, shipped_orders=shipped_orders, delivered_orders=delivered_orders, cart_items=cart_items, cart_total=cart_total, reviews=reviews)
        case _:
            print("ERROR ROUTING TO HOME")
            return "ERROR ROUTING TO HOME"

@views.route("/order/<int:order_id>", methods=["GET", "POST"])
@login_required
def order_manipulation(order_id):
    order = db.session.execute(text(f"SELECT * from Orders where order_id = {order_id};")).first()
    pending = request.form.get("pending")
    complete = request.form.get("complete")
    delete = request.form.get("delete")

    if request.form.get == "POST":
        if pending:
            db.session.execute(text(f"UPDATE Orders SET status = 'pending' WHERE order_id = {order_id};"))
            db.session.commit
        if complete:
            db.session.execute(text(f"UPDATE Orders SET status = 'shipped' WHERE order_id = {order_id};"))
            db.session.commit
        if delete:
            db.session.execute(text(f"DELETE FROM Orders WHERE order_id = {order_id};"))
            db.session.commit
    return render_template("order_choices.html", order=order)

@views.route("/vendor/add", methods=["GET"])
@login_required
def vendor_add():
    return render_template("vendor_add.html")

@views.route("/vendor/add", methods=["POST"])
@login_required
def add_items():
    title = request.form.get("title")
    description = request.form.get("description")
    product_image = request.files["product_image"]
    category = request.form.get("category")
    price = request.form.get("price")
    color = request.form.get("color")
    size = request.form.get("size")
    quantity = request.form.get("quantity")

    if product_image.filename == "":
        filename = ""
    else:
        filename = secure_filename(product_image.filename)
        product_image.save("website/static/uploads/" + filename)
    db.session.execute(text(f"INSERT INTO Products (title, description, product_image, category) VALUES ('{title}', '{description}', '{filename}', '{category}')"))
    db.session.commit()
    
    product = db.session.execute(text(f"SELECT * FROM Products WHERE product_id = LAST_INSERT_ID()")).first()
    vendor_id = db.session.execute(text(f"SELECT vendor_id FROM Vendors WHERE user_id = {current_user.user_id}")).first()

    db.session.execute(text(f"INSERT INTO Vendor_Products (product_id, vendor_id, qty, price) VALUES({product.product_id}, {vendor_id.vendor_id}, {quantity}, {price})"))
    db.session.commit()
    db.session.execute(text(f"INSERT INTO Vendor_Product_Sizes VALUES ({vendor_id.vendor_id}, '{size}')"))
    db.session.commit()
    db.session.execute(text(f"INSERT INTO Vendor_Product_Colors VALUES ({vendor_id.vendor_id}, '{color}')"))
    db.session.commit()
    
    return redirect(url_for("views.home"))
 
@views.route("/vendor/edit", methods=["GET"])
@login_required
def admin_edit():
    return render_template("vendor_edit.html")

@views.route("/vendor/edit", methods=["POST"])
@login_required
def edit_pick():
    vendor_products = db.session.execute(text(f"select product_id, title, product_image from Products WHERE product_id IN (select product_id from Vendor_Products where vendor_id = (select vendor_id from Vendors where user_id = {current_user.user_id}))")).all()
    return redirect(url_for("views.home"))

@views.route("/vendor/delete", methods=["GET"])
@login_required
def admin_delete():  
    return render_template("vendor_delete.html")

@views.route("/vendor/delete", methods=["POST"])
@login_required
def deletion():
    vendor = Vendor.query.filter_by(
    user_id=current_user.user_id).first()

    vendor_products = VendorProduct.query.filter_by(
    vendor_id=vendor.vendor_id).all()
    categories = [category[0].capitalize() for category in db.session.execute(text(f"SELECT category FROM Products where product_id IN (select product_id from Vendor_Products where vendor_id = (select vendor_id from Vendors where user_id = {current_user.user_id}))")).all()]
    categories.insert(0, "All")
    
    return redirect("/vendor/delete", vendor_products=vendor_products, categories=categories)


@views.route("/shop")
@login_required
def shop():
    categories = [category[0].capitalize() for category in
                  db.session.execute(text(f"SELECT DISTINCT category FROM Products ORDER BY category")).all()]

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
        f"SELECT * FROM Reviews JOIN Users USING(user_id) WHERE product_id={product_id}")).all()

    return render_template("product_page.html", title=title, description=description, product_image=product_image,
                           vendors=vendors, default_vendor=vendor_id, colors=colors, sizes=sizes, price=price,
                           vendor_product_id=vendor_product_id, reviews=reviews, product_id=product_id)


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
        return redirect(url_for("views.order_review", order_id=order.order_id))
    else:
        return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total)


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


@views.route("/complain", methods=["GET"])
@login_required
def complaints_page():
    return render_template("complaints_page.html")

@views.route("/complain", methods=["POST"])
def complaint_submit():
    title = request.form.get("title")
    user_id = current_user.user_id
    description = request.form.get("complaint")
    demand = request.form.get("demand")

    db.session.execute(text(f"INSERT INTO Complaints (user_id, title, description, demand) VALUES ({user_id}, '{title}', '{description}', '{demand}')"))
    db.session.commit()

    return redirect(url_for("views.home"))


@views.route("/order-review/<int:order_id>")
@login_required
def order_review(order_id):
    order = db.session.execute(text(f"SELECT * FROM Orders WHERE order_id={order_id}")).first()
    order_items = db.session.execute(text(f"SELECT Products.title AS title, Order_Items.qty AS qty, Order_Items.color AS color, Order_Items.size AS size, Vendor_Products.price AS price FROM Order_Items JOIN Vendor_Products USING(vendor_product_id) JOIN Products USING(product_id) WHERE order_id={order_id}")).all()
    total = 0
    for order_item in order_items.copy():
        total += order_item.price * order_item.qty
    
    return render_template("order_reviews.html", order=order, order_items=order_items, total=total)
   
    
@views.route("/review/<int:product_id>", methods=["POST"])
@login_required
def add_review(product_id):
    user_id = current_user.user_id
    rating = request.form.get("rating")
    message = request.form.get("message")
    image = request.files["image"]

    if image is None:
        filename = ""
    else:
        filename = secure_filename(image.filename)
        image.save("website/static/uploads/" + filename)
    
    db.session.execute(text(f"INSERT INTO Reviews (product_id, user_id, rating, message, image) VALUES ({product_id}, {user_id}, {rating}, '{message}', '{filename}')"))
    db.session.commit()
    
    return redirect(url_for("views.products_page", product_id=product_id))
