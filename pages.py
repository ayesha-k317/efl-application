from flask import Blueprint, current_app, render_template
import database

bp = Blueprint("pages", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/login")
def login_page():
    return render_template("login.html")

@bp.route("/converter")
def converter_page():
    return render_template("converter.html")

@bp.route("/quote-page")
def quote_page():
    plans = database.get_plans(current_app.config["DB_FILE"])
    return render_template("quote.html", plans=plans)

@bp.route("/history-page")
def history_page():
    return render_template("history.html")