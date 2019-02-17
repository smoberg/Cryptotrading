from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Orders(db.Model):
    API_key = db.Column(db.String(24), nullable=False)
    Order_id = db.Column(db.String(36), nullable=False, primary_key=True)
    Order_size = db.Column(db.Integer, nullable=False)
    Order_side = db.Column(db.String(4), nullable=False)
    Order_symbol = db.Column(db.String(10), nullable=False)
