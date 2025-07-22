from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
from config import db
from ..models import Answer

# Blueprint를 루트에 등록해서,
# /answers, /answers/user/<id>, /submit 등 모든 경로를 직접 선언합니다.
answers_blp = Blueprint('answers', __name__, url_prefix='')


def error_response(message: str, status_code: int):
    """모든 에러 응답을 {'message': ...} 형식으로 통일"""
    response = jsonify({'message': message})
    response.status_code = status_code
    return response


@answers_blp.route('/answers', methods=['POST'])
def create_answer():
    """
    단일 답변 생성
    POST /answers
    Body: { "user_id": int, "choice_id": int }
    """
    data = request.get_json()
    user_id = data.get('user_id')
    choice_id = data.get('choice_id')

    if not isinstance(user_id, int) or not isinstance(choice_id, int):
        return error_response('user_id와 choice_id는 정수로 전달되어야 합니다.', 400)

    try:
        answer = Answer(user_id=user_id, choice_id=choice_id)
        db.session.add(answer)
        db.session.commit()
        return jsonify({'id': answer.id}), 201

    except IntegrityError:
        db.session.rollback()
        return error_response('데이터베이스 무결성 오류', 400)

    except Exception as e:
        db.session.rollback()
        return error_response(f'서버 오류: {e}', 500)


@answers_blp.route('/answers', methods=['GET'])
def list_answers():
    """
    전체 답변 조회
    GET /answers
    """
    answers = Answer.query.order_by(Answer.id).all()
    result = [
        {'id': a.id, 'user_id': a.user_id, 'choice_id': a.choice_id}
        for a in answers
    ]
    return jsonify(result), 200


@answers_blp.route('/submit', methods=['POST'])
def submit_answers():
    """
    복수 답변 한 번에 저장
    POST /submit
    Body: [ { "user_id": int, "choice_id": int }, … ]
    """
    data = request.get_json()

    if not isinstance(data, list):
        return error_response('리스트 형식의 데이터를 보내주세요.', 400)

    try:
        user_id = None
        for idx, item in enumerate(data, start=1):
            # 형식 검증
            if (
                not isinstance(item, dict)
                or 'user_id' not in item
                or 'choice_id' not in item
            ):
                return error_response(f'Item #{idx}에 user_id와 choice_id가 포함되어야 합니다.', 400)

            uid = item['user_id']
            cid = item['choice_id']
            if not isinstance(uid, int) or not isinstance(cid, int):
                return error_response('user_id와 choice_id는 정수여야 합니다.', 400)

            # 모두 같은 user_id여야 함
            if user_id is None:
                user_id = uid
            elif user_id != uid:
                return error_response('모든 항목의 user_id는 동일해야 합니다.', 400)

            db.session.add(Answer(user_id=uid, choice_id=cid))

        db.session.commit()
        return jsonify({'message': f"User: {user_id}'s answers Success Create"}), 201

    except IntegrityError:
        db.session.rollback()
        return error_response('데이터베이스 무결성 오류', 400)

    except Exception as e:
        db.session.rollback()
        return error_response(f'서버 오류: {e}', 500)


@answers_blp.route('/answers/user/<int:user_id>', methods=['GET'])
def list_by_user(user_id: int):
    """
    특정 사용자 답변 조회
    GET /answers/user/<user_id>
    """
    answers = (
        Answer.query
        .filter_by(user_id=user_id)
        .order_by(Answer.id)
        .all()
    )
    if not answers:
        abort(404, description='해당 사용자의 답변이 없습니다.')

    result = [
        {'id': a.id, 'choice_id': a.choice_id}
        for a in answers
    ]
    return jsonify(result), 200
