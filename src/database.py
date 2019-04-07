from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), nullable=False, unique=True)
    api_public = db.Column(db.String(24), nullable=False)
    api_secret = db.Column(db.String(48), nullable=False)
    orders = db.relationship("Orders", back_populates="user")

class Orders(db.Model):
    order_id = db.Column(db.String(36), nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    order_size = db.Column(db.Integer, nullable=False)
    order_side = db.Column(db.String(4), nullable=False)
    order_symbol = db.Column(db.String(10), nullable=False)
    user = db.relationship("User", back_populates="orders")
