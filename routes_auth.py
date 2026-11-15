import sqlite3

from flask import Blueprint, current_app, jsonify, request, session

import auth
import database
import validators
from errors import InputError

bp = Blueprint("auth", __name__)

@bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    db_file = current_app.config["DB_FILE"]
    try:
        clean = validators.validate_registration(data)
        user_id = database.create_user(clean["name"], clean["email"], clean["phone"], auth.hash_password(clean["password"]), db_file)
    except InputError as error:
        return jsonify({"error": str(error)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"error": "An account with this email already exists."}), 400
    session.clear()
    session["user_id"] = user_id
    return jsonify({"name": clean["name"]}), 200

@bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    user = database.get_user_by_email(email, current_app.config["DB_FILE"])
    if user is None or not auth.check_password(password, user["password_hash"]):
        return jsonify({"error": "The email or password is incorrect."}), 401
    session.clear()
    session["user_id"] = user["user_id"]
    return jsonify({"name": user["name"]}), 200

@bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"signed_out": True}), 200