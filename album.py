from flask import Blueprint, jsonify

album_bp = Blueprint("album", __name__)

@album_bp.route("/albums", methods=["GET"])
def get_albums():
    return jsonify([
        {"id": 1, "title": "Sample Album 1"},
        {"id": 2, "title": "Sample Album 2"}
    ])