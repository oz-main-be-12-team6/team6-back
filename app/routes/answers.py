from flask import Blueprint, request, jsonify
from config import db
from app.models import Answer

# Blueprint 설정
answers_blp = Blueprint('answers', __name__)

# 1. 단일 답변 생성 (POST /answers)
@answers_blp.route('/answers', methods=['POST'])
def submit_answer():
    """
    JSON Body 예시:
    {
        "user_id": 1,
        "choice_id": 3
    }
    """
    data = request.get_json() or {}
    user_id = data.get('user_id')
    choice_id = data.get('choice_id')

    if user_id is None or choice_id is None:
        return jsonify({"error": "user_id와 choice_id는 필수입니다."}), 400

    try:
        # Answer 모델에 새 레코드 추가
        answer = Answer(user_id=user_id, choice_id=choice_id)
        db.session.add(answer)
        db.session.commit()
        return jsonify({
            "message": "답변이 저장되었습니다.",
            "id": answer.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 2. 전체 답변 조회 (GET /answers)
@answers_blp.route('/answers', methods=['GET'])
def get_all_answers():
    """모든 사용자 답변 리스트 조회"""
    try:
        answers = Answer.query.order_by(Answer.id).all()
        result = [
            {"id": a.id, "user_id": a.user_id, "choice_id": a.choice_id}
            for a in answers
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. 특정 사용자 답변 조회 (GET /answers/user/<user_id>)
@answers_blp.route('/answers/user/<int:user_id>', methods=['GET'])
def get_answers_by_user(user_id):
    """특정 사용자 답변 목록 조회"""
    try:
        answers = Answer.query.filter_by(user_id=user_id).order_by(Answer.id).all()
        result = [
            {"id": a.id, "choice_id": a.choice_id}
            for a in answers
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500