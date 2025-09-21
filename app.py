import os
from flask import Flask
from auth.routes import auth_bp
from products.routes import products_bp
from database import db  # Import db from your database.py file
from mail import mail
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS



# Create the Flask app instance
app = Flask(__name__)

# --- Configuration ---
# Set your configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root1234@localhost:3306/agrivetdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-super-secret-key'  # Change this!
app.config['JWT_SECRET_KEY'] = 'your-super-secret-jwt-key'  # Change this!


# Mailtrap Configuration
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'password-reset@agrivet.com'



# --- Initialize Extensions ---
# Initialize db with the app
db.init_app(app)
# Initialize JWT
jwt = JWTManager(app)
# Initialize Migrate
migrate = Migrate(app, db)
# Initialize Mail with the app
mail.init_app(app)
# Initialize CORS
CORS(app)

# --- Register Blueprints ---
app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)


# --- Main execution ---
if __name__ == '__main__':
    app.run(debug=True)