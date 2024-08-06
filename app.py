
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from models import Course  
        db.create_all()  
    from routes import course_bp
    app.register_blueprint(course_bp, url_prefix='/courses')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
