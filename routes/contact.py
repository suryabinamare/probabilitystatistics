from flask import Blueprint, render_template, request, redirect, url_for
from routes.database import get_db

contact_bp = Blueprint("contact", __name__, url_prefix="/contact")

@contact_bp.route("/", methods=["GET", "POST"])
def contact_form():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
            (
                request.form["name"],
                request.form["email"],
                request.form["message"]
            )
        )
        db.commit()
        return redirect(url_for("contact.contact_form"))

    return render_template("contact.html")
