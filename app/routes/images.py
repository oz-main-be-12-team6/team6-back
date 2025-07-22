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

    image_type = request.form.get('type', 'etc')  # 기본값

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
            'type': img.type
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
def create_image():
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


@images_blp.route('/main', methods=['GET'])
def get_main_image():
    image = Image.query.filter_by(type='main').order_by(Image.id.desc()).first()
    if not image:
        return jsonify({"image": None}), 404

    return jsonify({"image": image.url}), 200


