# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_cors import CORS
# import logging

# db = SQLAlchemy()
# migrate = Migrate()

# def create_app():
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Initialize CORS
#     CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

#     # Initialize extensions
#     db.init_app(app)
#     migrate.init_app(app, db)

#     # Register Blueprints
#     from routes import course_bp
#     app.register_blueprint(course_bp, url_prefix='/courses')

#     # Create database tables
#     with app.app_context():
#         db.create_all()

#     # Set up logging for debugging
#     logging.basicConfig(level=logging.DEBUG)

#     return app

# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True, port=5000)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import logging

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize CORS
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from routes import course_bp
    app.register_blueprint(course_bp, url_prefix='/courses')

    # Create database tables
    with app.app_context():
        db.create_all()

    # Set up logging for debugging
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('App initialized and running.')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
