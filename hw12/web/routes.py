"""
Flask routes for the anime recommendation agent web UI.
"""

from flask import Blueprint, jsonify, render_template, request, session

from agent.agent import process_query, clear_session
from config import config
from web.session_store import session_store

web_bp = Blueprint("web", __name__)


@web_bp.route("/", methods=["GET"])
def index():
    """Render the main page with chat interface."""
    return render_template("index.html")


@web_bp.route("/api/chat", methods=["POST"])
def chat():
    """Process a chat message and return the response."""
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    user_message = data["message"].strip()
    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    # Get or create session ID from Flask session
    if "session_id" not in session:
        session["session_id"] = session_store.create_session()
    session_id = session["session_id"]

    # Check for special commands
    if user_message.lower() == "/clear":
        clear_session(session_id)
        session_store.clear_session(session_id)
        return jsonify({
            "response": "История сессии очищена.",
            "history": [],
        })

    # Save user message to store
    session_store.add_message(session_id, "user", user_message)

    # Process through agent
    try:
        result = process_query(user_message, session_id=session_id)
        session_store.add_message(session_id, "assistant", result)
        return jsonify({
            "response": result,
            "history": session_store.get_history(session_id),
        })
    except Exception as e:
        error_msg = f"Ошибка обработки запроса: {str(e)}"
        session_store.add_message(session_id, "assistant", error_msg)
        return jsonify({
            "response": error_msg,
            "history": session_store.get_history(session_id),
        }), 500


@web_bp.route("/api/history", methods=["GET"])
def get_history():
    """Get chat history for the current session."""
    session_id = session.get("session_id")
    if not session_id:
        return jsonify({"history": []})
    return jsonify({"history": session_store.get_history(session_id)})


@web_bp.route("/api/clear", methods=["POST"])
def clear():
    """Clear the current session."""
    session_id = session.get("session_id")
    if session_id:
        clear_session(session_id)
        session_store.clear_session(session_id)
    return jsonify({"status": "cleared"})