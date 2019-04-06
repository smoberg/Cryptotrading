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
    def add_control_account(self):
        self.add_control("account", href=api.url_for(AccountInformation),
                        method="GET",
                        title="Get general account information")

    def add_control_orders(self):
        self.add_control("orders", href=api.url_for(OrdersResource),
                        method="GET",
                        title="Get open orders")

    def add_control_orderbook(self):
        self.add_control("orderbook", href=api.url_for(OrderBook),
                        method="GET",
                        title="Get order book data")

    def add_control_priceaction(self):
        self.add_control("priceaction", href=api.url_for(PriceAction),
                        method="GET",
                        title="Show recent trades that happened in the market")

    def add_control_positions(self):
        self.add_control("positions", href=api.url_for(Positions),
                        method="GET",
                        title="Get open positions")

#apikeyt pitää lisätä
@app.route("/", methods=["GET"])
def entrypoint():
    body = MasonControls()
    body.add_control_account()
    body.add_control_orders()
    body.add_control_orderbook()
    body.add_control_priceaction()
    body.add_control_positions()
    return Response(json.dumps(body), status=200, mimetype=MASON)

class AccountInformation(Resource):
    def get(self, apikey):
        return Response(apikey, status=503)

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


api.add_resource(AccountInformation,"/account/")
api.add_resource(OrdersResource,"/orders/")
api.add_resource(PriceAction, "/priceaction/")
api.add_resource(Positions, "/positions/")
api.add_resource(OrderBook, "/orderbook/")


def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
