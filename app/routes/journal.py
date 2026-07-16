from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import JournalEntry
from app.safety import CRISIS_RESOURCE_MESSAGE
from app.risk_model import predict_risk

journal_bp = Blueprint("journal", __name__, url_prefix="/api/journal")


@journal_bp.route("", methods=["GET"])
@jwt_required()
def list_entries():
    user_id = get_jwt_identity()
    entries = (
        JournalEntry.query.filter_by(user_id=user_id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )
    return jsonify([e.to_dict() for e in entries]), 200


@journal_bp.route("", methods=["POST"])
@jwt_required()
def create_entry():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "content is required"}), 400

    # Run the trained model instead of the old keyword check
    risk_label, confidence = predict_risk(content)

    entry = JournalEntry(
        user_id=user_id,
        content=content,
        risk_label=risk_label,
        risk_score=confidence,
    )
    db.session.add(entry)
    db.session.commit()

    response = {"entry": entry.to_dict()}

    # Surface crisis resources when the model flags high concern
    if risk_label == "high":
        response["crisis_flag"] = True
        response["support_message"] = CRISIS_RESOURCE_MESSAGE
    else:
        response["crisis_flag"] = False

    return jsonify(response), 201