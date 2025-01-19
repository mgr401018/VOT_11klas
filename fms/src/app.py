from flask import Flask, request, jsonify
from minio import Minio
from minio.error import S3Error
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from keycloak import KeycloakOpenID
import os

app = Flask(__name__)

# Configuration
KEYCLOAK_SERVER_URL = 'http://keycloak:8080/realms/fms_realm'
KEYCLOAK_CLIENT_ID = 'fms_client'
KEYCLOAK_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0w2jWO5YvD7IYBmhxsFTco4EK03i/+Ozqg+Z+RP9qJuQNbaZu+M5McCTMa0y31Ijba1Fbe0s/fHgaqKGMrbM+ofeQk2/qPLzeDJMPalTwGsVfBPxTwrncP18n/3okicEhGBq+NX9J5Ymy/TorNh7w4YYeQVTMp+NvdZwDu0XuS/dnc9NrBsjA6nngEs3aDR5FPFPiLL7HZzoL6Zfpwkb1VlzMfsq+pis1p8YrrD8oG3Gycm5AbJR+VLw0nxNS2N9SK1JKvxYc+nyoQSsACMADxOkt4Q8ptwPVHM4eamxC1ZOXjQPD5Ac1UmC9aDa/NFckVhAMlGIfck/JkERsf5NXQIDAQAB
-----END PUBLIC KEY-----
"""
KEYCLOAK_CLIENT_SECRET = 'AxA7Ai8g68RdB0gzIwamXEfoCUw4cYpL'
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_PUBLIC_KEY'] = KEYCLOAK_PUBLIC_KEY

jwt = JWTManager(app)
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    realm_name='fms_realm'
)

minio_client = Minio(
    os.getenv("MINIO_URL", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "minioadmin"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minioadmin"),
    secure=False
)

BUCKET_NAME = "mybucket"
if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"error": "No file provided"}), 400

    try:
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)  # Reset file pointer to the beginning

        minio_client.put_object(BUCKET_NAME, file.filename, file, file_length)
        return jsonify({"message": f"File '{file.filename}' uploaded successfully."}), 200
    except S3Error as err:
        return jsonify({"error": str(err)}), 500


@app.route('/download/<file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    try:
        file = minio_client.get_object(BUCKET_NAME, file_id)
        return file.read(), 200
    except S3Error as err:
        return jsonify({"error": str(err)}), 500

@app.route('/update/<file_id>', methods=['PUT'])
@jwt_required()
def update_file(file_id):
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file provided"}), 400

    try:
        minio_client.put_object(BUCKET_NAME, file_id, file, file.seek(0, os.SEEK_END))
        return jsonify({"message": f"File '{file_id}' updated successfully."}), 200
    except S3Error as err:
        return jsonify({"error": str(err)}), 500

@app.route('/delete/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    try:
        minio_client.remove_object(BUCKET_NAME, file_id)
        return jsonify({"message": f"File '{file_id}' deleted successfully."}), 200
    except S3Error as err:
        return jsonify({"error": str(err)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
