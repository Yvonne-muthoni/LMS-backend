import re
import json
from app import app, db
from models import Course



def get_youtube_thumbnail_url(video_url):
    # Regex to extract YouTube video ID from different URL 
    youtube_id_match = re.search(r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|v\/|embed\/|user\/\S+\/\S+\/|embed\/|\S+\/\S+\/|v\/)|youtu\.be\/|youtube\.com\/(?:playlist\?list=|embed\/|v\/|watch\?v=))([a-zA-Z0-9_-]{11})', video_url)
    if youtube_id_match:
        video_id = youtube_id_match.group(1)
        return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    return None



def seed_database():
    with app.app_context():
        db.create_all()
        
    
        courses = [
            {
                "title": "Introduction to Python",
                "description": "Learn the basics of Python programming, including syntax, data structures, and basic algorithms.",
                "video": "https://www.youtube.com/watch?v=rfscVS0vtbw",
                "tech_stack": "Python,Flask,SQLAlchemy",
                "what_you_will_learn": json.dumps([
                    "Understand Python syntax and semantics",
                    "Implement basic algorithms and data structures",
                    "Work with Flask to create web applications"
                ])
            },
            {
                "title": "Mastering JavaScript",
                "description": "Dive deep into JavaScript and learn how to build dynamic, responsive web applications.",
                "video": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
                "tech_stack": "JavaScript,React,Node.js,Express",
                "what_you_will_learn": json.dumps([
                    "Advanced JavaScript concepts and ES6 features",
                    "Building single-page applications with React",
                    "Backend development with Node.js and Express"
                ])
            },
            {
                "title": "Full-Stack Web Development",
                "description": "A comprehensive course covering both front-end and back-end web development technologies.",
                "video": "https://www.youtube.com/watch?v=Q33KBiDriJY",
                "tech_stack": "HTML,CSS,JavaScript,Python,Django,PostgreSQL",
                "what_you_will_learn": json.dumps([
                    "Design and build full-stack web applications",
                    "Implement responsive design using HTML and CSS",
                    "Develop RESTful APIs with Django and PostgreSQL"
                ])
            },
            {
                "title": "Data Science with Python",
                "description": "Explore the world of data science using Python, including data analysis, visualization, and machine learning.",
                "video": "https://www.youtube.com/watch?v=ua-CiDNNj30",
                "tech_stack": "Python,Pandas,NumPy,Matplotlib,Scikit-learn",
                "what_you_will_learn": json.dumps([
                    "Data manipulation and analysis with Pandas",
                    "Data visualization with Matplotlib and Seaborn",
                    "Machine learning algorithms and model evaluation"
                ])
            },

                        {
                "title": "Mastering JavaScript",
                "description": "Dive deep into JavaScript and learn how to build dynamic, responsive web applications.",
                "video": "https://www.youtube.com/watch?v=PkZNo7MFNFg",
                "tech_stack": "JavaScript,React,Node.js,Express",
                "what_you_will_learn": json.dumps([
                    "Advanced JavaScript concepts and ES6 features",
                    "Building single-page applications with React",
                    "Backend development with Node.js and Express"
                ])
            },
        ]
        
        # Insert data
        for course_data in courses:
            thumbnail_url = get_youtube_thumbnail_url(course_data["video"])
            if not thumbnail_url:
                # Fallback if thumbnail URL extraction fails
                thumbnail_url = "https://example.com/image/default_thumbnail.jpg"
            
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                image=thumbnail_url,
                video=course_data["video"],
                tech_stack=course_data["tech_stack"],
                what_you_will_learn=course_data["what_you_will_learn"]
            )
            db.session.add(course)
        
        db.session.commit()

if __name__ == "__main__":
    seed_database()
