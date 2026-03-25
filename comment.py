import sqlite3
from flask import Blueprint, request, jsonify, current_app

comment_bp = Blueprint("comment", __name__)


def get_db_connection():
    conn = sqlite3.connect(current_app.config["DB_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


@comment_bp.route("/api/comments", methods=["GET"])
def get_comments():
    post_id = request.args.get("postId")

    conn = get_db_connection()

    if post_id:
        comments = conn.execute(
            "SELECT * FROM comments WHERE post_id = ? ORDER BY id DESC",
            (post_id,)
        ).fetchall()
    else:
        comments = conn.execute("SELECT * FROM comments ORDER BY id DESC").fetchall()

    conn.close()

    result = []
    for comment in comments:
        result.append({
            "id": comment["id"],
            "post_id": comment["post_id"],
            "name": comment["name"],
            "body": comment["body"]
        })

    return jsonify(result)


@comment_bp.route("/api/comments", methods=["POST"])
def create_comment():
    data = request.get_json()

    post_id = data.get("post_id")
    name = data.get("name")
    body = data.get("body")

    if not post_id or not name or not body:
        return jsonify({"error": "post_id, name and body are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO comments (post_id, name, body)
        VALUES (?, ?, ?)
    """, (post_id, name, body))

    conn.commit()
    comment_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Comment added successfully",
        "id": comment_id
    }), 201


@comment_bp.route("/api/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    conn = get_db_connection()
    comment = conn.execute(
        "SELECT * FROM comments WHERE id = ?",
        (comment_id,)
    ).fetchone()

    if not comment:
        conn.close()
        return jsonify({"error": "Comment not found"}), 404

    conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Comment deleted successfully"})