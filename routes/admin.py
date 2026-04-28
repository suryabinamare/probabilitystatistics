from flask import Blueprint, render_template, request, redirect, url_for, session
from routes.database import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# ---- LOGIN ----
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (
            request.form["username"] == "suryathapamagar" and
            request.form["password"] == "thapamagar123"
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))

    return render_template("admin_login.html")

# ---- DASHBOARD ----
@admin_bp.route("/dashboard")
def dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin.login"))

    db = get_db()
    contacts = db.execute(
        "SELECT * FROM contacts ORDER BY created_at DESC"
    ).fetchall()

    return render_template("admin_dashboard.html", contacts=contacts)

# ---- LOGOUT ----
@admin_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))
