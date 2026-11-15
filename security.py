from flask import jsonify, redirect, request, session

PUBLIC_ENDPOINTS = {"pages.index", "pages.login_page", "auth.register", "auth.login", "static"}

def current_user_id():
    """Return the signed-in user's id."""
    return session["user_id"]

def require_login():
    """Block every route that is not public unless the user is signed in."""
    if request.endpoint in PUBLIC_ENDPOINTS:
        return None
    if "user_id" in session:
        return None
    if request.path.startswith("/api/"):
        return jsonify({"error": "Please sign in first."}), 401
    return redirect("/login")

def add_security_headers(response):
    """Ask the browser to apply safe defaults."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Cache-Control"] = "no-store"
    return response