from flask import Blueprint, jsonify, request
from app.models import Question, Choices
from config import db

questions_blp = Blueprint('questions', __name__, url_prefix='/questions')


@questions_blp.route('/<int:question_sqe>', methods=['GET'])
def get_question_by_sqe(question_sqe):
    """
    GET /questions/<int:question_sqe>
    설명: sqe 기준으로 질문 1개 + 선택지 배열 반환
    """
    question = Question.query.filter_by(sqe=question_sqe, is_active=True).first()

    if not question:
        return jsonify({"error": "존재하지 않는 질문입니다."}), 404

    choices = Choices.query.filter_by(question_id=question.id, is_active=True).order_by(Choices.sqe).all()

    return jsonify({
        "id": question.id,
        "title": question.title,
        "image": question.image.url if question.image else None,
        "choices": [c.to_dict() for c in choices]
    }), 200


@questions_blp.route('/count', methods=['GET'])
def question_count():
    """
    GET /questions/count
    설명: 전체 질문 개수 반환
    """
    total = Question.query.filter_by(is_active=True).count()
    return jsonify({"total": total})


@questions_blp.route('/question', methods=['POST'])
def create_question():
    """
    POST /question
    설명: 새 질문 등록
    """
    data = request.get_json(force=True)
    try:
        question = Question(
            title=data['title'],
            sqe=data['sqe'],
            image_id=data['image_id'],
            is_active=data.get('is_active', True)
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({
            "message": f"Title: {question.title} question Success Create"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
