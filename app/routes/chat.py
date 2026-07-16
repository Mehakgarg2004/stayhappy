from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from groq import Groq
from app.extensions import db
from app.models import ChatMessage
from app.safety import check_crisis_flag, CRISIS_RESOURCE_MESSAGE

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

SYSTEM_PROMPT = (
    "You are a warm, empathetic support companion inside a mental wellness app called StayHappy. "
    "You are NOT a therapist or doctor and must never diagnose or give clinical advice. "
    "Keep responses supportive, non-judgmental, and conversational — a few sentences, not an essay. "
    "Encourage healthy coping and, when appropriate, gently suggest professional support without being pushy."
)


@chat_bp.route("", methods=["POST"])
@jwt_required()
def send_message():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "message is required"}), 400

    # Save the user's message
    user_msg = ChatMessage(user_id=user_id, role="user", content=message)
    db.session.add(user_msg)
    db.session.commit()

    # Safety check BEFORE calling the LLM — crisis handling should never depend on model output
    if check_crisis_flag(message):
        reply_text = CRISIS_RESOURCE_MESSAGE
        assistant_msg = ChatMessage(user_id=user_id, role="assistant", content=reply_text)
        db.session.add(assistant_msg)
        db.session.commit()
        return jsonify({"reply": reply_text, "crisis_flag": True}), 200

    # Pull recent chat history for context (last 10 messages)
    recent = (
        ChatMessage.query.filter_by(user_id=user_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
        .all()
    )
    recent.reverse()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in recent:
        messages.append({"role": m.role, "content": m.content})

    client = Groq(api_key=current_app.config["GROQ_API_KEY"])
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=300,
    )
    reply_text = completion.choices[0].message.content

    assistant_msg = ChatMessage(user_id=user_id, role="assistant", content=reply_text)
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({"reply": reply_text, "crisis_flag": False}), 200


@chat_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    messages = (
        ChatMessage.query.filter_by(user_id=user_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return jsonify([
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in messages
    ]), 200