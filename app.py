import os
import sqlite3
from flask import Flask, send_from_directory, redirect
from flask_cors import CORS

from post import post_bp
from comment import comment_bp
from album import album_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
CORS(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["DB_PATH"] = DB_PATH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            image TEXT,
            category TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            body TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
    """)

    conn.commit()
    conn.close()


init_db()

app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)
app.register_blueprint(album_bp)


@app.route("/")
def home():
    return redirect("/posts")


@app.route("/posts")
def posts_page():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/style.css")
def css():
    return send_from_directory(app.static_folder, "style.css")


@app.route("/main.js")
def js():
    return send_from_directory(app.static_folder, "main.js")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
