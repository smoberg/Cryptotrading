from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Orders(db.Model):
    API_key = db.Column(db.String, nullable=False)
    Order_id = db.Column(db.String, nullable=False)
    Order_size = db.Column(db.Integer)
    Order_side = db.Column(db.String)
    Order_symbol = db.Column(db.String)
