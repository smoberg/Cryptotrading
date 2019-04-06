from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError
from flask_restful import Resource, Api
from jsonschema import validate, ValidationError
from utils import MasonBuilder
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)

class MasonControls(MasonBuilder):
    # attaches mason hypermedia controls to response bodies
    def add_control_asd(self):
        pass
