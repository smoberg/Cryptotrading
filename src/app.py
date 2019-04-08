from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError
from flask_restful import Resource, Api
from jsonschema import validate, ValidationError
from utils import MasonBuilder
import json
from bitmex_websocket import BitMEXWebsocket
from database import db, User, Orders

MASON = "application/vnd.mason+json"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)
db.init_app(app)
with app.app_context():
    db.create_all()

class MasonControls(MasonBuilder):
    # attaches mason hypermedia controls to response bodies
    @staticmethod
    def account_schema():
        schema = {
            "type": "object",
            "required": ["accountname", "api_public", "api_secret"]
        }
        props = schema["properties"] = {}
        props["accountname"] = {
            "description": "name of the account",
            "type": "string"
        }
        props["api_public"] = {
            "description": "public part of the api-key",
            "type": "string"
        }

        props["api_secret"] = {
            "description": "secret part of the api-key",
            "type": "string"
        }
        return schema

    def add_control_account(self, apikey):
        self.add_control("account", href=api.url_for(AccountInformation, apikey=apikey),
                        method="GET",
                        title="Get general account information")

    def add_control_orders(self, apikey):
        self.add_control("orders", href=api.url_for(OrdersResource, apikey=apikey),
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

    def add_control_positions(self, apikey):
        self.add_control("positions", href=api.url_for(Positions, apikey=apikey),
                        method="GET",
                        title="Get open positions")

    def add_control_accountbalance(self, apikey):
        self.add_control("balance", href=api.url_for(AccountBalance, apikey=apikey),
                        method="GET",
                        title="Get account balance")

    def add_control_transactionhistory(self, apikey):
        self.add_control("transactions", href=api.url_for(TransactionHistory, apikey=apikey),
                        method="GET",
                        title="Get history of the wallet transactions")

    def add_control_add_account(self):
        self.add_control("add-account", href=api.url_for(Account),
                        method="POST",
                        encoding="json",
                        title="add account to cryptotrading api",
                        schema=self.account_schema())

    def add_control_delete_account(self, apikey):
        self.add_control("delete", href=api.url_for(AccountInformation, apikey=apikey),
                        method="DELETE",
                        title="delete this account")


@app.route("/", methods=["GET"])
def entrypoint():
    body = MasonControls()
    body.add_control_add_account()
    # body.add_control_orders()
    body.add_control_orderbook()
    body.add_control_priceaction()
    # body.add_control_positions()
    return Response(json.dumps(body), status=200, mimetype=MASON)

class Account(Resource):
    def get(self):
        # add control to entrypoint maybe
        body = MasonControls()
        body.add_control_add_account()
        return Response(json.dumps(body), status=200, mimetype=MASON)

    def post(self):
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, MasonControls.account_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        user = User(username=request.json["accountname"], api_public=request.json["api_public"],
                        api_secret=request.json["api_secret"])
        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            return create_error_response(409, "Already exists",
                                        "Account with name '{}' already exists.".format(request.json["accountname"]))
        return Response(status=201, headers={"Location": api.url_for(AccountInformation, apikey=request.json["api_public"])})

class AccountInformation(Resource):
    def get(self, apikey):
        # sends request to bitmex websocket api, retrieves Response
        # Parses response
        # Adds json controls to body
        # Return response
        # pitääköhä olla controlli takasin entrypointtii?
        acc = User.query.filter_by(api_public=apikey).first()
        if not acc:
            return create_error_response(404, "Account does not exist", "Account with api-key '{}' does not exist.".format(apikey))
        # authorized = authorize(acc, request)
        if not authorize(acc, request):
            return create_error_response(401, "Unauthorized", "need secret api-key in the http header")
        body = MasonControls(accountname=acc.username, api_public=acc.api_public, api_secret=acc.api_secret)
        body.add_control("self", api.url_for(AccountInformation, apikey=apikey))
        body.add_control_orders(apikey)
        body.add_control_accountbalance(apikey)
        body.add_control_positions(apikey)
        body.add_control_transactionhistory(apikey)
        body.add_control_delete_account(apikey)
        return Response(json.dumps(body), status=200, mimetype=MASON)

    def delete(self, apikey):
        acc = User.query.filter_by(api_public=apikey).first()
        if not acc:
            return create_error_response(404, "Account does not exist", "Account with api-key '{}' does not exist.".format(apikey))
        authorize(acc, request)
        db.session.delete(acc)
        db.session.commit()
        return Response(status=204)


def authorize(model, request):
    # takes in user model and request object
    # compares request object's api key to the saved api key in the database
    try:
         secret = request.headers["api_secret"]
    except KeyError:
        return False
    if secret != model.api_secret:
        return False
    else:
        return True

class AccountBalance(Resource):
    def get(self):


        body = MasonControls()
        body.add_control_account()
        body.add_control_transactionhistory()
        return Response(body, status=200, mimetype=MASON)

class TransactionHistory(Resource):
    def get(self):


        body = MasonControls()
        body.add_control_account()
        body.add_control_accountbalance()
        return Response(body, status=200, mimetype=MASON)

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

api.add_resource(Account,"/account/")
api.add_resource(AccountInformation,"/account/<apikey>")
api.add_resource(OrdersResource,"/orders/<apikey>")
api.add_resource(PriceAction, "/priceaction/")
api.add_resource(Positions, "/positions/<apikey>")
api.add_resource(OrderBook, "/orderbook/")
api.add_resource(TransactionHistory, "/account/history/<apikey>")
api.add_resource(AccountBalance, "/account/balance/<apikey>")

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    # body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
