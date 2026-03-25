import os
import sqlite3
import requests
from uuid import uuid4
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

post_bp = Blueprint("post", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def get_db_connection():
    conn = sqlite3.connect(current_app.config["DB_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@post_bp.route("/api/posts", methods=["GET"])
def get_posts():
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    conn.close()

    result = []
    for post in posts:
        result.append({
            "id": post["id"],
            "user_id": post["user_id"],
            "title": post["title"],
            "body": post["body"],
            "image": post["image"],
            "category": post["category"]
        })
    return jsonify(result)


@post_bp.route("/api/posts/<int:post_id>", methods=["GET"])
def get_single_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()

    if not post:
        return jsonify({"error": "Post not found"}), 404

    return jsonify({
        "id": post["id"],
        "user_id": post["user_id"],
        "title": post["title"],
        "body": post["body"],
        "image": post["image"],
        "category": post["category"]
    })


@post_bp.route("/api/posts", methods=["POST"])
def create_post():
    user_id = request.form.get("user_id")
    title = request.form.get("title")
    body = request.form.get("body")
    category = request.form.get("category")
    image_file = request.files.get("image")

    if not user_id or not title or not body:
        return jsonify({"error": "user_id, title and body are required"}), 400

    image_url = None

    if image_file and image_file.filename:
        if not allowed_file(image_file.filename):
            return jsonify({"error": "Invalid image format"}), 400

        ext = image_file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid4().hex}.{ext}"
        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            secure_filename(filename)
        )
        image_file.save(filepath)
        image_url = f"http://127.0.0.1:5000/uploads/{filename}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (user_id, title, body, image, category)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, title, body, image_url, category))
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Post created successfully",
        "id": post_id,
        "image": image_url
    }), 201


@post_bp.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    conn = get_db_connection()
    post = conn.execute(
        "SELECT * FROM posts WHERE id = ?",
        (post_id,)
    ).fetchone()

    if not post:
        conn.close()
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json()

    user_id = data.get("user_id", post["user_id"])
    title = data.get("title", post["title"])
    body = data.get("body", post["body"])
    category = data.get("category", post["category"])
    image = data.get("image", post["image"])

    conn.execute("""
        UPDATE posts
        SET user_id = ?, title = ?, body = ?, image = ?, category = ?
        WHERE id = ?
    """, (user_id, title, body, image, category, post_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Post updated successfully"})


@post_bp.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    conn = get_db_connection()
    post = conn.execute(
        "SELECT * FROM posts WHERE id = ?",
        (post_id,)
    ).fetchone()

    if not post:
        conn.close()
        return jsonify({"error": "Post not found"}), 404

    conn.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Post deleted successfully"})


@post_bp.route("/seed-jsonplaceholder", methods=["POST"])
def seed_jsonplaceholder_posts():
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts?_limit=25")
        response.raise_for_status()
        posts = response.json()

        conn = get_db_connection()
        cursor = conn.cursor()

        inserted_count = 0

        for post in posts:
            existing = conn.execute(
                "SELECT id FROM posts WHERE user_id = ? AND title = ? AND body = ?",
                (post["userId"], post["title"], post["body"])
            ).fetchone()

            if not existing:
                cursor.execute("""
                    INSERT INTO posts (user_id, title, body, image, category)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    post["userId"],
                    post["title"],
                    post["body"],
                    None,
                    "JSONPlaceholder"
                ))
                inserted_count += 1

        conn.commit()
        conn.close()

        return jsonify({
            "message": f"{inserted_count} posts inserted successfully"
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500