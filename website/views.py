from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("design-concept.html")