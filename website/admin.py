from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import text
from .models import *


admin = Blueprint('admin', __name__)
