from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Users, Teachers, Students
from . import db
from flask_login import login_user, login_required, logout_user, current_user


# This file will need some work. We need to hash the passwords instead of using plan-text


auth = Blueprint('auth', __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = Users.query.filter_by(email=email).first()
        if user:
            if password == user.password:
                teacher = Teachers.query.filter_by(
                    user_id=user.user_id).first()
                if teacher:
                    login_user(teacher, remember=True)
                else:
                    student = Students.query.filter_by(
                        user_id=user.user_id).first()
                    login_user(student, remember=True)
                return redirect(url_for('views.tests'))
            else:
                flash("Incorrect Password, try again!")
        else:
            flash(
                "No account associated with that email.")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        teacher_account = True if request.form.get(
            "teacher") == "on" else False

        user = Users.query.filter_by(username=username).first()
        if user:
            flash("Username already exists")
        else:
            user = Users.query.filter_by(email=email).first()
            if user:
                flash("email already exists")
            else:
                new_user = Users(username=username,
                                 email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                if teacher_account:
                    new_teacher = Teachers(user_id=new_user.user_id)
                    db.session.add(new_teacher)
                    db.session.commit()
                    login_user(new_teacher, remember=True)
                else:
                    new_student = Students(user_id=new_user.user_id)
                    db.session.add(new_student)
                    db.session.commit()
                    login_user(new_student, remember=True)
                return redirect(url_for('views.tests'))

    return render_template("register.html")
