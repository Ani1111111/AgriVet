from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import db
from auth.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    required = {'name', 'email', 'password'}
    if not required.issubset(data):
        return jsonify({"error": "name, email, password are required"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed = generate_password_hash(data['password'])
    user = User(
        name=data['name'].strip(),
        email=data['email'].strip().lower(),
        password=hashed,
        role=data.get('role', 'customer')  # for dev; later restrict this
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"}), 201


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if not {'email', 'password'}.issubset(data):
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=data['email'].strip().lower()).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))  # create JWT token
    return jsonify({
        "message": "Login successful",
        "access_token": token  # return it here
    }), 200


@auth_bp.route('/users/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }), 200
