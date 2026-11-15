import os
import traceback

from flask import Flask, jsonify, render_template, request, session
from werkzeug.exceptions import HTTPException

import config
import database
import diagnostics
import pages
import routes_auth
import routes_convert
import routes_history
import routes_quotes
import security

app = Flask(__name__)
app.config["DB_FILE"] = config.DB_FILE
app.secret_key = os.environ.get("EFL_SECRET_KEY", config.DEV_SECRET_KEY)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.register_blueprint(pages.bp)
app.register_blueprint(routes_auth.bp)
app.register_blueprint(routes_convert.bp)
app.register_blueprint(routes_quotes.bp)
app.register_blueprint(routes_history.bp)

app.before_request(security.require_login)
app.after_request(security.add_security_headers)

@app.errorhandler(Exception)
def handle_internal_error(error):
    if isinstance(error, HTTPException):
        if request.path.startswith("/api/"):
            return jsonify({"error": error.description}), error.code
        return render_template("error.html", message=error.description), error.code
    db_file = app.config["DB_FILE"]
    diagnostics.log_error_to_db(request.path, traceback.format_exc(), db_file)
    user_id = session.get("user_id")
    saved_note = ""
    draft_id = None
    data = request.get_json(silent=True) or request.form.to_dict()
    if data:
        diagnostics.cache_user_data(user_id, data)
        saved_note = " Your entries have been saved."
        if user_id is not None:
            try:
                draft_id = database.save_draft(user_id, data, db_file)
            except Exception:
                draft_id = None
    message = "Something went wrong on our side." + saved_note + " Please try again."
    if request.path.startswith("/api/"):
        return jsonify({"error": message, "draft_id": draft_id}), 500
    return render_template("error.html", message=message), 500

if __name__ == "__main__":
    app.run(debug=True)