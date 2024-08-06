
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import requests

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # Enable CORS for the app

    # Import models here to avoid circular imports
    with app.app_context():
        import models  # Ensure models are imported after db is initialized

    # Register blueprints
    from routes import course_bp, enrollment_bp, student_bp
    app.register_blueprint(course_bp, url_prefix='/courses')
    app.register_blueprint(enrollment_bp, url_prefix='/enrollments')
    app.register_blueprint(student_bp, url_prefix='/students')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
