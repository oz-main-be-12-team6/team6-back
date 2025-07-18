from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename

images_bp = Blueprint('images', __name__, url_prefix='/images')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@images_bp.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config.get('UPLOAD_FOLDER', './static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 201
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@images_bp.route('/', methods=['GET'])
def list_images():
    upload_folder = current_app.config.get('UPLOAD_FOLDER', './static/uploads')
    if not os.path.exists(upload_folder):
        return jsonify({'images': []})

    files = os.listdir(upload_folder)
    images = []
    for f in files:
        if allowed_file(f):
            # 요청 호스트 URL + 정적 파일 경로를 붙여서 이미지 URL 생성
            image_url = f"{request.host_url}static/uploads/{f}"
            images.append({'filename': f, 'url': image_url})
    return jsonify({'images': images})

@images_bp.route('/<filename>', methods=['DELETE'])
def delete_image(filename):
    upload_folder = current_app.config.get('UPLOAD_FOLDER', './static/uploads')
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': f'{filename} deleted successfully'})
    else:
        return jsonify({'error': 'File not found'}), 404
