from flask import Blueprint, jsonify, request, abort
from Persistence.DBStorage import storage
from Models.themeModel import Theme
from Models.userModel import User


theme_bp = Blueprint("themes", __name__, url_prefix="/api/themes")


# ************************************************
# GET ALL THEMES
# ************************************************
@admin_required
@theme_bp.route("/", methods=["GET"])
def get_themes():
    themes = storage.all(Theme)
    return jsonify([t.to_dict() for t in themes.values()]), 200


# ************************************************
# GET THEME BY ID
# ************************************************
@admin_required
@theme_bp.route("/<theme_id>", methods=["GET"])
def get_theme(theme_id):
    theme = storage.get(Theme, theme_id)
    if not theme:
        abort(404, description="Theme not found")
    return jsonify(theme.to_dict()), 200


# ************************************************
# CREATE THEME
# ************************************************
@auth_required
@theme_bp.route("/", methods=["POST"])
def create_theme():
    if not request.is_json:
        abort(400, description="Not a JSON")

    data = request.get_json()
    required = ["name", "keywords", "user_id"]

    for field in required:
        if field not in data:
            abort(400, description=f"Missing {field}")

    user = storage.get(User, data["user_id"])
    if not user:
        abort(404, description="User not found")

    theme = Theme(
        name=data["name"],
        keywords=data["keywords"],
        description=data.get("description"),
        user_id=data["user_id"]
    )

    storage.new(theme)
    storage.save()

    return jsonify(theme.to_dict()), 201


# ************************************************
# UPDATE THEME
# ************************************************
@auth_required
@theme_bp.route("/<theme_id>", methods=["PUT"])
def update_theme(theme_id):
    theme = storage.get(Theme, theme_id)
    if not theme:
        abort(404)

    if not request.is_json:
        abort(400, description="Not a JSON")

    ignore = ["id", "user_id", "created_at", "updated_at", "deleted_at"]

    for key, value in request.json.items():
        if key not in ignore and hasattr(theme, key):
            setattr(theme, key, value)

    theme.update_timestamp()
    storage.save()

    return jsonify(theme.to_dict()), 200


# ************************************************
# DELETE THEME
# ************************************************
@admin_required
@theme_bp.route("/<theme_id>", methods=["DELETE"])
def delete_theme(theme_id):
    theme = storage.get(Theme, theme_id)
    if not theme:
        abort(404)

    storage.delete(theme)
    storage.save()
    return jsonify({}), 200
