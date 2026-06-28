"""
app.py — WildLens Flask application.

Routes:
    /            -> upload page (must be logged in)
    /signup      -> create account
    /login       -> log in
    /logout      -> log out
    /predict     -> POST image, run model, save + show result
    /history     -> view past predictions
"""

import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import db
from model_utils import predict_image
from species_info import get_species_info

app = Flask(__name__)
app.secret_key = "change-this-to-something-random-and-secret"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(view):
    """Simple decorator: redirect to login if no user_id in session."""
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


# ---------------- AUTH ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Enter both a username and password.")
            return render_template("signup.html")

        password_hash = generate_password_hash(password)
        success = db.create_user(username, password_hash)

        if success:
            flash("Account created. You can log in now.")
            return redirect(url_for("login"))
        else:
            flash("That username is already taken.")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = db.get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            flash("Incorrect username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- MAIN PAGES ----------------

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session.get("username"))


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if "image" not in request.files:
        flash("No image selected.")
        return redirect(url_for("index"))

    file = request.files["image"]

    if file.filename == "" or not allowed_file(file.filename):
        flash("Please upload a .png or .jpg image.")
        return redirect(url_for("index"))

    # Save with a unique name so two users' uploads never collide
    safe_name = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(save_path)

    # Run the model
    results = predict_image(save_path, top_n=3)
    top_result = results[0]

    # Look up real-world info about the top prediction (Wikipedia)
    species_info = get_species_info(top_result["label"])

    # Save the top prediction to this user's history
    db.save_prediction(
        user_id=session["user_id"],
        image_filename=unique_name,
        predicted_label=top_result["label"],
        confidence=top_result["confidence"],
    )

    return render_template(
        "index.html",
        username=session.get("username"),
        results=results,
        image_url=url_for("static", filename=f"uploads/{unique_name}"),
        species_info=species_info,
    )


@app.route("/history")
@login_required
def history():
    records = db.get_history_for_user(session["user_id"])
    return render_template("history.html", records=records, username=session.get("username"))


if __name__ == "__main__":
    app.run(debug=True)
