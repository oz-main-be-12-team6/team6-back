from flask import Blueprint, jsonify, request
from app.models import Question, Choices
from config import db

questions_blp = Blueprint('questions', __name__, url_prefix='/questions')


@questions_blp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    question = Question.query.filter_by(id=question_id, is_active=True).first()

    if not question:
        return jsonify({"error": "존재하지 않는 질문입니다."}), 404

    choices = Choices.query.filter_by(question_id=question.id, is_active=True).order_by(Choices.sqe).all()

    return jsonify({
        "id": question.id,
        "title": question.title,
        "image": question.image.to_dict() if question.image else None,
        "choices": [c.to_dict() for c in choices]
    })


@questions_blp.route('/count', methods=['GET'])
def question_count():
    total = Question.query.filter_by(is_active=True).count()
    return jsonify({"total": total})


@questions_blp.route('', methods=['POST'])
def create_question():
    data = request.get_json()
    question = Question(
        title=data['title'],
        sqe=data['sqe'],
        image_id=data['image_id'],
        is_active=True
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({"id": question.id}), 201
