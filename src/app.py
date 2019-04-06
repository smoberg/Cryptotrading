from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError
from flask_restful import Resource, Api
from jsonschema import validate, ValidationError
from utils import MasonBuilder
import json

MASON = "application/vnd.mason+json"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)

class MasonControls(MasonBuilder):
    # attaches mason hypermedia controls to response bodies
    def add_control_asd(self):
        pass

api.add_resource(AccountInformation,"/account/{apikey}")
api.add_resource(Orders,"/orders/{apikey}")
api.add_resource(PriceAction, "/priceaction/")
api.add_resource(Positions, "positions/{apikey}")
api.add_resource(OrderBook, "/orderbook/")

@app.route("/", methods=["GET"])
def entrypoint():
    body = MasonControls()
    return Response(json.dumps(body), status=200, mimetype=MASON)

class AccountInformation(Resource):
    def get(self):
        return Response(status=503)

class AccountBalance(Resource):
    def get(self):
        return Response(status=503)

class TransactionHistory(Resource):
    def get(self):
        return Response(status=503)

class OrdersResource(Resource):
    def get(self):
        return Response(status=503)

class OrderResource(Resource):
    def get(self):
        return Response(status=503)

class OrderHistory(Resource):
    def get(self):
        return Response(status=503)

class OrderBook(Resource):
    def get(self):
        return Response(status=503)

class PriceAction(Resource):
    def get(self):
        return Response(status=503)

class BucketedPriceAction(Resource):
    def get(self):
        return Response(status=503)

class Positions(Resource):
    def get(self):
        return Response(status=503)

class Position(Resource):
    def get(self):
        return Response(status=503)

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
