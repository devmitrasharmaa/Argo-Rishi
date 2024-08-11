import enum
from flask_login import UserMixin
from . import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Farmers.query.get(user_id)

from sqlalchemy import Enum

# Define the categories as an Enum
class PostCategory(enum.Enum):
    pulses = "Pulses"
    vegetation = "Vegetation"
    grains = "Grains"
    fruits = "Fruits"
    vegetables = "Vegetables"
    herbs = "Herbs"
    others= "Others"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(200), nullable=False)  # Changed to String with a limit
    description = db.Column(db.Text, nullable=True)  # New field for detailed description
    category = db.Column(db.Enum(PostCategory), nullable=False)  # New field for category
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('farmers.id'), nullable=False)
    upvotes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"Post('{self.caption}', '{self.category}', '{self.date_posted}')"

class Farmers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)
