from flask import Blueprint, render_template
from .help import login_required

admin = Blueprint('admin', __name__)

@admin.route("/account")
@login_required
def account():
    return render_template("account.html")