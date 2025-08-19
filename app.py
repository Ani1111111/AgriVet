from flask import Flask
from auth.routes import auth_bp
from database import db

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sql12790898:94Cg8zqiXn@sql12.freesqldatabase.com/sql12790898'
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this in production

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates tables on first run
    app.run(debug=True)
