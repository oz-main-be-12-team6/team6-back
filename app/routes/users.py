from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from app.models import User, AgeStatus, GenderStatus
from config import db

user_blp = Blueprint("users", __name__)

@user_blp.route("/", methods=["GET"])
def connect():
    return jsonify({"message": "Success Connect"})

@user_blp.route("/signup", methods=["POST"])
def signup_page():
    if not request.is_json:
        return jsonify({"message": "요청은 JSON 형식이어야 합니다."}), 400

    data = request.get_json()

    # 필수 항목 체크
    required_fields = ["name", "age", "gender", "email"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"필수 입력 항목이 없습니다: {field}"}), 400

    try:
        # Enum 타입으로 변환 (입력값이 올바른지 검증)
        age_enum = AgeStatus(data["age"])
        gender_enum = GenderStatus(data["gender"])
    except ValueError:
        return jsonify({"message": "age 또는 gender 값이 올바르지 않습니다."}), 400

    try:
        user = User(
            name=data["name"],
            age=age_enum,
            gender=gender_enum,
            email=data["email"],
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": f"{user.name}님 회원가입을 축하합니다",
            "user_id": user.id,
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "이미 존재하는 이메일 입니다."}), 400
