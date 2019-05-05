from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, DataError
from flask_restful import Resource, Api
from jsonschema import validate, ValidationError
from utils import MasonBuilder
import json
from bitmex_websocket import BitMEXWebsocket

MASON = "application/vnd.mason+json"
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
api = Api(app)
# ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD", api_key=None, api_secret=None)

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

    def add_control_accountbalance(self):
        self.add_control("balance", href=api.url_for(AccountBalance),
                        method="GET",
                        title="Get account balance")

    def add_control_transactionhistory(self):
        self.add_control("transactions", href=api.url_for(TransactionHistory),
                        method="GET",
                        title="Get history of the wallet transactions")


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
    def get(self):
        # sends request to bitmex websocket api, retrieves Response
        # Parses response
        # Adds json controls to body
        # Return response
        # pitääköhä olla controlli takasin entrypointtii?

        body = MasonControls()
        body.add_control_orders()
        body.add_control_accountbalance()
        body.add_control_positions()
        body.add_control_transactionhistory()

        return Response(body, status=200, mimetype=MASON)

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
        if not request.args:
            return create_error_response(400, "Query Error", 'Missing Query Parameter "symbol"')
        try:
            if request.args["symbol"]:
                ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol=request.args["symbol"], api_key=None, api_secret=None)
                trades = []
                trades = ws.recent_trades()
                for trade in trades:
                    trade.pop("timestamp")
                    trade.pop("tickDirection")
                    trade.pop("trdMatchID")
                    trade.pop("homeNotional")
                    trade.pop("foreignNotional")
                    trade.pop("grossValue")

                return Response(json.dumps(trades), status=200, mimetype="application/json")
        except:
            return create_error_response(400, "Query Error", "Query Parameter doesn't exist")

class BucketedPriceAction(Resource):
    def get(self):
        return Response(status=503)

class Positions(Resource):
    def get(self):

        try:
            ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD", api_key="79z47uUikMoPe2eADqfJzRBu", api_secret="j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd")
            positions = []
            parsed_positions = []
            positions = ws.positions()
            for position in positions:
                parsed_position = {}
                parsed_position["symbol"] = position["symbol"]
                parsed_position["size"] = position["currentQty"]
                if position["crossMargin"] == True:
                    parsed_position["leverage"] = 0
                else:
                    parsed_position["leverage"] = position["leverage"]
                parsed_position["entryprice"] = position["avgEntryPrice"]
                parsed_position["liquidationprice"] = position["liquidationPrice"]
                parsed_positions.append(parsed_position)
            return Response(json.dumps(parsed_positions), status=200, mimetype="application/json")
        except TypeError:
            return create_error_response(400, "Query Error", "Query Parameter doesn't exist")


class Position(Resource):
    def get(self):
            if not request.args["symbol"]:
                create_error_response(400, "Query Error", 'Missing query parameter "symbol"')
            try:
                ws = BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD", api_key="79z47uUikMoPe2eADqfJzRBu", api_secret="j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd")
                parsed_positions = []
                positions = ws.positions()
                for position in positions:
                    parsed_position = {}
                    parsed_position["symbol"] = position["symbol"]
                    parsed_position["size"] = position["currentQty"]
                    if position["crossMargin"] == True:
                        parsed_position["leverage"] = 0
                    else:
                        parsed_position["leverage"] = position["leverage"]
                    parsed_position["entryprice"] = position["avgEntryPrice"]
                    parsed_position["liquidationprice"] = position["liquidationPrice"]
                    parsed_positions.append(parsed_position)
                return Response(json.dumps(parsed_positions), status=200, mimetype="application/json")
            except TypeError:
                return create_error_response(400, "Query Error", "Query Parameter doesn't exist")


api.add_resource(AccountInformation,"/account/")
api.add_resource(OrdersResource,"/orders/")
api.add_resource(PriceAction, "/priceaction/")
api.add_resource(Positions, "/positions/")
api.add_resource(OrderBook, "/orderbook/")
api.add_resource(TransactionHistory, "/account/history/")
api.add_resource(AccountBalance, "/account/balance/")

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    #body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)
