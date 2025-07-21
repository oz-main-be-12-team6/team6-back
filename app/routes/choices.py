from flask import Blueprint, jsonify
from app.models import Choices

choices_blp = Blueprint("choices", __name__, url_prefix="/choices")


@choices_blp.route("/question/<int:question_id>", methods=["GET"])
def get_choices_by_question(question_id):
    choices = Choices.query.filter_by(question_id=question_id).order_by(Choices.sqe).all()

    result = [choice.to_dict() for choice in choices]

    return jsonify({"choices": result})