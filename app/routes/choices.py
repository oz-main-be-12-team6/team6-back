from flask import Blueprint, jsonify, request
from app.models import Choices
from config import db

choices_blp = Blueprint("choices", __name__, url_prefix="/choices")


@choices_blp.route("/question/<int:question_id>", methods=["GET"])
def get_choices_by_question(question_id):
    choices = Choices.query.filter_by(question_id=question_id, is_active=True).order_by(Choices.sqe).all()
    result = [choice.to_dict() for choice in choices]
    return jsonify({"choices": result})


@choices_blp.route('', methods=['POST'])
def create_choice():
    data = request.get_json()
    choice = Choices(
        content=data['content'],
        sqe=data['sqe'],
        question_id=data['question_id'],
        is_active=data.get('is_active', True)
    )
    db.session.add(choice)
    db.session.commit()
    return jsonify({"id": choice.id}), 201


@choices_blp.route('/choice', methods=['POST'])
def create_choice_alias_for_guideline():
    """
    POST /choice - 가이드라인에 맞춘 alias
    """
    return create_choice()
