from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from sqlalchemy import text
from .models import *

views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template("index.html")


@views.route('/home')
def home():
    return render_template("design-concept.html")