from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import db
from auth.models import User
# --- Imports for Forgot Password ---
from mail import mail
from flask import current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer


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


# --- Route for Forgot Password ---
def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"error": "Email is required"}), 400

    email = data['email'].strip().lower()
    user = User.query.filter_by(email=email).first()

    if user:
        token = generate_reset_token(email)
        reset_url = f"http://your-frontend-url.com/reset-password?token={token}"
        
        msg = Message(
            subject="Password Reset Request for AgriVet",
            recipients=[user.email],
            body=f"To reset your password, please click the following link: {reset_url}",
            html=f"<p>To reset your password, please click the link below:</p><p><a href='{reset_url}'>Reset Password</a></p>"
        )
        mail.send(msg)

    return jsonify({"message": "If an account with that email exists, a password reset link has been sent."}), 200


def verify_reset_token(token, max_age_seconds=3600):
    """
    Verifies the password reset token.
    Returns the email if the token is valid, otherwise None.
    'max_age_seconds' is how long the token is valid for (default: 1 hour).
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt='password-reset-salt',
            max_age=max_age_seconds
        )
    except Exception:
        return None
    return email


@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    if not data or 'token' not in data or 'new_password' not in data:
        return jsonify({"error": "Token and new password are required"}), 400

    token = data['token']
    new_password = data['new_password']

    # Verify the token
    email = verify_reset_token(token)
    if not email:
        return jsonify({"error": "The reset token is invalid or has expired."}), 400

    # Find the user and update their password
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({"message": "Your password has been successfully updated."}), 200
    
    return jsonify({"error": "User not found."}), 404