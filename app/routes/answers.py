from flask import Blueprint, request, jsonify
from app.models import Answer
from config import db

answers_blp = Blueprint("answers", __name__)

@answers_blp.route("/submit", methods=["POST"])
def submit_answer():
    """
    Request Body:
    [
      { "user_id": 1, "choice_id": 2 },
      { "user_id": 1, "choice_id": 4 }
    ]

    Response:
    {
      "message": "User: 1's answers Success Create"
    }
    """
    data = request.get_json()
    try:
        answers = [Answer(user_id=i["user_id"], choice_id=i["choice_id"]) for i in data]
        db.session.add_all(answers)
        db.session.commit()
        return jsonify({"message": f"User: {data[0]['user_id']}'s answers Success Create"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400
