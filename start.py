from flask import Flask

# Create the Flask application instance
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return 'Hello! Welcome to the home page.'


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
