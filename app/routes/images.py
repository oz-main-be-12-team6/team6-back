from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.models import Image  # SQLAlchemy 모델
from config import db        # DB 세션

images_blp = Blueprint('images', __name__, url_prefix='/images')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@images_blp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    image_type = request.form.get('type', 'etc')  # 기본값 'etc'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        upload_folder = current_app.config.get('UPLOAD_FOLDER', './static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        image_url = f"{request.host_url}static/uploads/{filename}"

        image = Image(url=image_url, type=image_type)
        db.session.add(image)
        db.session.commit()

        return jsonify({
            'message': 'File uploaded and saved to DB successfully',
            'filename': filename,
            'url': image_url,
            'id': image.id,
            'type': image_type
        }), 201
    else:
        return jsonify({'error': 'File type not allowed'}), 400


@images_blp.route('/', methods=['GET'])
def list_images():
    images = Image.query.all()
    results = []
    for img in images:
        results.append({
            'id': img.id,
            'url': img.url,
            'type': img.type.value if hasattr(img.type, "value") else img.type
        })
    return jsonify({'images': results})


@images_blp.route('/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    image = Image.query.get(image_id)
    if not image:
        return jsonify({'error': 'Image not found'}), 404

    try:
        filename = os.path.basename(image.url)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', './static/uploads')
        file_path = os.path.join(upload_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        return jsonify({'error': f'File delete error: {str(e)}'}), 500

    db.session.delete(image)
    db.session.commit()

    return jsonify({'message': f'Image id {image_id} and file deleted successfully'})


@images_blp.route('/type/<image_type>', methods=['GET'])
def get_images_by_type(image_type):
    images = Image.query.filter_by(type=image_type).all()
    results = [{'id': img.id, 'url': img.url} for img in images]
    return jsonify({'images': results})

@images_blp.route('', methods=['POST'])
def create_image_direct():
    data = request.get_json(force=True)

    url = data.get('url')
    image_type = data.get('type')

    if not url or not image_type:
        return jsonify({'error': 'url과 type은 필수입니다.'}), 400

    try:
        image = Image(url=url, type=image_type)
        db.session.add(image)
        db.session.commit()

        return jsonify({
            'message': f"ID: {image.id} Image Success Create"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ———————————————————————
# 설문조사 이미지 + 이름 데이터 API (미리 하드코딩된 데이터 반환)
# ———————————————————————

@images_blp.route('/survey-data', methods=['GET'])
def survey_data():
    # 1번 문항 : 치킨 브랜드
    brands = [
        {"name": "BHC", "url": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAxODA3MjFfMTUw%2FMDAxNTMyMTE3NjI3MDYw.TENjgNTXdckMknwwuyOcWr3xhSgz"},
        {"name": "BBQ", "url": "https://post-phinf.pstatic.net/MjAxODAzMDFfMTAz/MDAxNTIxNzQxOTI1NjA5.Z9d6iIrfOEcVQzXoovQ0kSTWwsU3x1Bf7Yl-kjAf-cwg.WlcyypvEjkSL1X-LCR5Coo4IgQ87q8W17Mk6MVEZ8wIg.JPEG/IMG_3191.jpg?type=w1200"},
        {"name": "굽네치킨", "url": "https://post-phinf.pstatic.net/MjAxOTA4MDFfMjc4/MDAxNTY0NDc3NDM0Mjc0.LlyeXkCNmLErTfTkNGw4bwpb5xhDdrIDKOD_9Uo0H2cg.kcjAg_d5EluWVLd8QIBSNIV4X_RUbJ6OkXe_LrddH4kg.JPEG/image_9932784721569084313626.jpg?type=w1200"},
        {"name": "자담치킨", "url": "https://blog.kakaocdn.net/dn/cDx4tX/btqTIEeOuhN/I2KE4U1VkxQinG2X5Yq5Yk/img.jpg"},
    ]

    # 2번 문항 : 치킨 종류
    types = [
        {"name": "후라이드", "url": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2F20140619_267%2Fkangdh83_1403144828833lBRmG_JPEG%2F20140511_134450.jpg"},
        {"name": "양념", "url": "https://post-phinf.pstatic.net/MjAxOTA0MTBfMTQw/MDAxNTU0NzY4MjU0NTkz.2D2YXYLkTVxnGwVveOHN5pijM9bQ7sYc4D8nCflqyoEg.qDEaBLu34Twx1_sT3FYYZgWwAJ4eJXAtX6SOZoY-2c4g.JPEG/image_1122845031553717960417.jpg?type=w1200"},
        {"name": "간장", "url": "https://post-phinf.pstatic.net/MjAxOTA1MTNfMTI1/MDAxNTU3MjgxODUxNDM2.0h-Jsm3v0T99yzv4q9KlHTNKRIH8EeEy5RO9EvUSkRUg.ZMHHKe-jbWdOLo75CFoDjDkYKwOTllHdRtFDrtyAlPwg.JPEG/image_1321255909765190508401.jpg?type=w1200"},
        {"name": "반반", "url": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAxNzExMTFfMjgy%2FMDAxNTEwMTk1ODc1ODQx.yvghosHd2uMXG91lcJQ2j1e2qV8heLeCnSi8EZZnqVkg.1Mz3YDwQ49PTwX72UlyvMJ5HaSLmcw2CuItn6x-VtOAg.JPEG.oppodev%2FIMG_4107.JPG"},
        {"name": "로스트", "url": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAxNjA4MDZfNjEg%2FMDAxNDcwNTg2MjQ5OTI2.X5WVLRm5c92Iy88kgqzRs4TlN5BRc2Muav5JHeSv2kIg.8Xo7AQ2UaaFQv_3XK9weRnz-tRuK6g0VcsLCEuZQm1bIg.JPEG.sporfishing%2FIMG_3079.JPG"},
    ]

    # 3번 문항 : 음료/사이드
    sides = [
        {"name": "콜라", "url": "https://post-phinf.pstatic.net/MjAxODA0MjBfNjEg/MDAxNTIyNjI2Mzg5MzYy.0TNVTh5x19GhxXB2zEZd7o8nuVhu0mHLauWNjTeq3TQg.XWdiXzNcDnKedYZUw9bXqH_lOMlVkoe6N1G_xHAtAQKg.JPEG/image_121856088581623005226.jpg?type=w1200"},
        {"name": "맥주", "url": "https://post-phinf.pstatic.net/MjAxNzExMTBfMTk1/MDAxNTEwMTE5NjQwNzE0.Hsy9bFkQFqbmvUoW8aTJIVNc7DcLMguj1bzPLVb-w-kg.V29TtpVqn4FpA6lhifvUhtZgfI6H1p_mnnEb1xG89YYMg.JPEG.kanoyuki%2FIMG_0070.JPG"},
        {"name": "치즈볼", "url": "https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2F20141002_227%2Fhello4455_1412214423263Mvrs2_JPEG%2F20141002_174838.jpg"},
        {"name": "감자튀김", "url": "https://post-phinf.pstatic.net/MjAxOTA0MTFfMTM0/MDAxNTU1MjU1NzQ2NjQw.o1AAYT_qK3fMPacDqW5e_WEdZ6qY8iDH0qZq0cJMuTcg.RcA6FDKlLxHwM__dGUCNgnV3vWhImh_v1TNYKOT1-TEg.JPEG/image_1413439608377322355939.jpg?type=w1200"},
    ]

    return jsonify({
        "brands": brands,
        "types": types,
        "sides": sides
    })
