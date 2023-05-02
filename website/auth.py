from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Admin, Vendor, Customer
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Incorrect Password, try again!")
        else:
            flash("No account associated with that email.")

    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        user_type = request.form.get("user_type")

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already taken!")
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                flash("Email already taken")
            else:
                new_user = User(username=username, name=name,
                                email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                match user_type:
                    case "Customer":
                        new_customer = Customer(user_id=new_user.user_id)
                        db.session.add(new_customer)
                        db.session.commit()
                    case "Vendor":
                        new_vendor = Vendor(user_id=new_user.user_id)
                        db.session.add(new_vendor)
                        db.session.commit()
                    case "Admin":
                        new_admin = Admin(user_id=new_user.user_id)
                        db.session.add(new_admin)
                        db.session.commit()
                    case _:
                        print("THERE WAS AN ERROR WITH THE REGISTRATION!")
                login_user(new_user, remember=True)
                return redirect(url_for("views.home"))

    return render_template("register.html")
