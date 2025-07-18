from flask import Blueprint, jsonify, request

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')

@questions_bp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    if question_id < 1 or question_id > 5:
        return jsonify({"error": "존재하지 않는 질문입니다."}), 404

    question = {
        "id": question_id,
        "title": f"{question_id}번 질문입니다",
        "image": f"https://example.com/question{question_id}.jpg",
        "choices": []
    }

    for choice_id in range(1, 6):
        choice = {
            "id": choice_id,
            "content": f"{question_id}번 질문의 선택지 {choice_id}",
            "is_active": True,
            "sqe": choice_id,
            "question_id": question_id
        }
        question["choices"].append(choice)

    @questions_bp.route('/count', methods=['GET'])
    def qeustion_count():
        total = Question.query.count()

        return jsonify({"total": total})

    return jsonify(question)