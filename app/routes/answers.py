
# app/routes/answers.py

from flask import request, Blueprint, jsonify
from sqlalchemy.exc import IntegrityError
from app.models import Answer
from config import db

answers_blp = Blueprint("answers", __name__)


@answers_blp.route("/submit", methods=["POST"])
def submit_answer():
    """
    POST /submit
    Body: [
      {"user_id": 1, "choice_id": 2},
      {"user_id": 1, "choice_id": 4}
    ]
    """
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"message": "Request body must be a list"}), 400

    try:
        user_id = None

        for idx, item in enumerate(data, start=1):
            # 각 항목이 dict 형태인지 검증
            if not isinstance(item, dict):
                return jsonify({"message": f"Item #{idx} must be an object"}), 400

            # 필수 필드 존재 여부 확인
            if "user_id" not in item or "choice_id" not in item:
                missing = "user_id" if "user_id" not in item else "choice_id"
                return jsonify({"message": f"Missing required field: {missing}"}), 400

            uid, cid = item["user_id"], item["choice_id"]

            # 타입 검증
            if not isinstance(uid, int) or not isinstance(cid, int):
                return jsonify({"message": "user_id and choice_id must be integers"}), 400

            # 모두 동일한 user_id인지 확인
            if user_id is None:
                user_id = uid
            elif user_id != uid:
                return jsonify({"message": "All items must have the same user_id"}), 400
            answer = Answer(user_id=item['user_id'], choice_id=item['choice_id'])
            db.session.add(answer)

        db.session.commit()
        return jsonify({"message": f"User: {user_id}'s answers Success Create"}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Database integrity error"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Server error: {e}"}), 500