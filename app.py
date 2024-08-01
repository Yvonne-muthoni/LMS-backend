# from flask import Flask, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# import requests
# from flask_cors import CORS

# db = SQLAlchemy()
# migrate = Migrate()

# def create_app():
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     db.init_app(app)
#     migrate.init_app(app, db)
#     CORS(app)  # Enable CORS for the app

#     # Import models here to avoid circular imports
#     with app.app_context():
#         import models  # Ensure models are imported after db is initialized

#     # Register blueprints
#     from routes import course_bp, enrollment_bp, student_bp  # Ensure blueprints are imported
#     app.register_blueprint(course_bp, url_prefix='/courses')
#     app.register_blueprint(enrollment_bp, url_prefix='/enrollments')
#     app.register_blueprint(student_bp, url_prefix='/students')

#     # Add YouTube API route
#     @app.route('/youtube_videos', methods=['GET'])
#     def youtube_videos():
#         api_key = 'AIzaSyAuu1LOJKCFPEg1dXLAYgL5DrUOFgSMbP4'
#         search_query = 'learning python,javascript,Html'
#         max_results = 700
#         search_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&maxResults={max_results}&type=video&key={api_key}'
        
#         response = requests.get(search_url)
#         if response.status_code == 200:
#             videos = response.json().get('items', [])
#             video_data = []
#             for video in videos:
#                 video_id = video['id']['videoId']
#                 video_title = video['snippet']['title']
#                 video_description = video['snippet']['description']
#                 video_url = f'https://www.youtube.com/watch?v={video_id}'
#                 video_data.append({
#                     'id': video_id,
#                     'title': video_title,
#                     'description': video_description,
#                     'url': video_url
#                 })
#             return jsonify(video_data)
#         else:
#             return jsonify({'error': 'Failed to fetch videos'}), response.status_code

#     return app

# if __name__ == '__main__':
#     app = create_app()
#     app.run(debug=True)
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
