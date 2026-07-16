from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import MoodLog

mood_bp = Blueprint("mood", __name__, url_prefix="/api/mood")


@mood_bp.route("", methods=["GET"])
@jwt_required()
def list_moods():
    user_id = int(get_jwt_identity())
    logs = (
        MoodLog.query.filter_by(user_id=user_id)
        .order_by(MoodLog.created_at.desc())
        .all()
    )
    return jsonify([m.to_dict() for m in logs]), 200


@mood_bp.route("", methods=["POST"])
@jwt_required()
def log_mood():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    score = data.get("score")
    tags = data.get("tags", [])

    if not isinstance(score, int) or not (1 <= score <= 10):
        return jsonify({"error": "score must be an integer from 1 to 10"}), 400

    log = MoodLog(user_id=user_id, score=score, tags=",".join(tags) if tags else None)
    db.session.add(log)
    db.session.commit()

    return jsonify(log.to_dict()), 201


@mood_bp.route("/trend", methods=["GET"])
@jwt_required()
def mood_trend():
    """Returns mood logs formatted for a Chart.js line chart (Phase 4)."""
    user_id = int(get_jwt_identity())
    logs = (
        MoodLog.query.filter_by(user_id=user_id)
        .order_by(MoodLog.created_at.asc())
        .all()
    )
    return jsonify({
        "labels": [m.created_at.strftime("%Y-%m-%d %H:%M") for m in logs],
        "scores": [m.score for m in logs],
    }), 200
