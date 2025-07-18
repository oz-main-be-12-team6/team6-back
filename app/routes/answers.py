from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
from config import db
from app.models import Answer

# Blueprint 설정 (url_prefix로 중복 방지)
answers_blp = Blueprint('answers', __name__, url_prefix='/answers')


def error_response(message: str, status_code: int):
    """표준화된 에러 응답"""
    response = jsonify({'error': message})
    response.status_code = status_code
    return response


@answers_blp.route('', methods=['POST'])
def create_answer():
    """
    단일 답변 생성
    JSON Body 예시:
    {
        "user_id": 1,
        "choice_id": 3
    }
    """
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    choice_id = data.get('choice_id')

    # 입력 검증
    if not isinstance(user_id, int) or not isinstance(choice_id, int):
        return error_response('user_id와 choice_id는 정수로 전달되어야 합니다.', 400)

    try:
        answer = Answer(user_id=user_id, choice_id=choice_id)
        db.session.add(answer)
        db.session.commit()
        return jsonify({'id': answer.id}), 201

    except IntegrityError as e:
        db.session.rollback()
        return error_response('데이터베이스 무결성 오류', 400)

    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)


@answers_blp.route('', methods=['GET'])
def list_answers():
    """모든 답변 조회 (필요시 페이징 추가)"""
    answers = Answer.query.order_by(Answer.id).all()
    result = [
        {
            'id': a.id,
            'user_id': a.user_id,
            'choice_id': a.choice_id
        }
        for a in answers
    ]
    return jsonify(result), 200


@answers_blp.route('/user/<int:user_id>', methods=['GET'])
def list_by_user(user_id: int):
    """특정 사용자 답변 조회"""
    answers = Answer.query.filter_by(user_id=user_id).order_by(Answer.id).all()
    if not answers:
        abort(404, description='해당 사용자의 답변이 없습니다.')

    result = [
        {
            'id': a.id,
            'choice_id': a.choice_id
        }
        for a in answers
    ]
    return jsonify(result), 200