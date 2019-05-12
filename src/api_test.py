import pytest
import tempfile
import os
from app import app
from database import User, Orders, db
from sqlalchemy.engine import Engine
from sqlalchemy import event
import json
from jsonschema import validate


"""
These tests are based on the api testing example introduce in the course material

"""

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def client():
    """ creates app fixture for testing """
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True
    app.config["DEBUG"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        _populate_db()

        yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    """ Populates database with three users each with one order """
    with app.app_context():
        for i in range(1, 4):
            user=User(username="testuser-{}".format(i),
                      api_public="79z47uUikMoPe2eADqfJzRB{}".format(i),
                      api_secret="j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd")

            order = Orders(order_id='00000000-0000-0000-0000-00000000000{}'.format(i),
                           order_price=3567.5, order_size=1, order_side='Buy',
                           order_symbol="XBTUSD")

            user.orders.append(order)
            db.session.add(user)
        # adds a real user that has valid apikey for bitmex related stuff
        user=User(username="realuser",
                  api_public="79z47uUikMoPe2eADqfJzRBu",
                  api_secret="j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd")

        order = Orders(order_id='00000000-0000-0000-0000-000000000000',
                       order_price=3567.5, order_size=1, order_side='Buy',
                       order_symbol="XBTUSD")
        user.orders.append(order)
        db.session.add(user)
        db.session.commit()


def _check_control_get_method(ctrl, client, obj, headers=None):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    if headers:
        resp = client.get(href, headers=headers)
        assert resp.status_code == 200
    else:
        resp = client.get(href)
        assert resp.status_code == 200

def _check_control_delete_method(ctrl, client, obj, headers=None):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    if headers:
        resp = client.delete(href, headers=headers)
        assert resp.status_code == 204
    else:
        resp = client.delete(href)
        assert resp.status_code == 204

def _check_control_post_method(ctrl, client, obj, headers=None):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid account/order against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    if ctrl == "add-account":
        body = _get_account_json()
    if ctrl == "add-order":
        body = _get_order_json()
    validate(body, schema)
    if headers:
        resp = client.post(href, json=body, headers=headers)
        assert resp.status_code == 201
    else:
        resp = client.post(href, json=body)
        assert resp.status_code == 201

def _check_control_patch_method(ctrl, client, obj, headers=None):
    """
    Checks a PATCH type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204. After the test changes leverage back to 1 for the other tests
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "patch"
    assert encoding == "json"
    body = _get_leverage_json()
    validate(body, schema)
    resp = client.patch(href, json=body, headers=headers)
    assert resp.status_code == 204
    # change it back for other test
    body = {"leverage": 1}
    resp = client.patch(href, json=body, headers=headers)
    assert resp.status_code == 204

def _get_account_json(number=1):
    """ Creates account json object that is used in POST account test """
    return {"accountname": "user{}".format(number),
	       "api_public": "79z47uUikMoPe2eADqfJzR{}B".format(number),
	       "api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}

def _get_order_json():
    """ Creates order json object that is used in POST order test """
    return {
            "price": 3837.5,
            "symbol": "XBTUSD",
            "side": "Buy",
            "size": 20
            }

def _get_leverage_json():
    """ Creates leverage json object that is used in PATCH position test """
    return {"leverage": 2}


class TestAccounts(object):

    RESOURCE_URL = "/accounts/"
    VALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}

    def test_get(self, client):
        """
        Tests the Get method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Also checks that all of the items from
        the DB popluation are present, and their controls. To simplify testing
        same secret apikey works for every account in the database.
        """
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_control_post_method("add-account", client, body)
        assert len(body["items"]) == 4
        for item in body["items"]:
            _check_control_get_method("self", client, item, headers=self.VALID_API_SECRET)
            assert "accountname" in item
            assert "api_public" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """
        valid = _get_account_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["api_public"] + "/")
        resp = client.get(resp.headers["Location"], headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["accountname"] == "user1"
        assert body["api_public"] == "79z47uUikMoPe2eADqfJzR1B"
        assert body["api_secret"] == "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"

        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # remove accountname field for 400
        valid.pop("accountname")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

class TestAccount(object):
    RESOURCE_URL = "/accounts/79z47uUikMoPe2eADqfJzRBu/"
    INVALID_URL = "/accounts/79z47uUikMoPe2eADqfJzR69/"
    VALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}
    INVALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8G123"}

    def test_get(self, client):
        """
        Tests the Get method. Checks that the response status code is 200, and
        then checks that all of the expected attributes and controls are
        present, and the controls work. Checks also that correct error responses
        happen.
        """
        # send with wrong api_secret for 401
        resp = client.get(self.RESOURCE_URL, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        # invalid url for 404
        resp = client.get(self.INVALID_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        # get with valid api_secret
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["accountname"] == "realuser"
        assert body["api_public"] == "79z47uUikMoPe2eADqfJzRBu"
        assert body["api_secret"] == "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"

        _check_control_get_method("orders-all", client, body, headers=self.VALID_API_SECRET)
        # gets stuck because the apikey used in the request is not valid apikey that is used in bitmex
        _check_control_get_method("positions-all", client, body, headers=self.VALID_API_SECRET)
        _check_control_get_method("accounts-all", client, body)
        _check_control_delete_method("delete", client, body, headers=self.VALID_API_SECRET)

    def test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request receives 204
        response and that trying to GET the account afterwards gives 404.
        Also checks that trying to delete an account that doesn't exist results
        in 404. Also checks that user has sufficient permission to delete.
        """
        # Send with wrong api_secret for 401
        resp = client.delete(self.RESOURCE_URL, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        resp = client.delete(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        resp = client.delete(self.INVALID_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

class TestOrders(object):
    RESOURCE_URL = "/accounts/79z47uUikMoPe2eADqfJzRBu/orders/"
    INVALID_URL = "/accounts/79z47uUikMoPe2eADqfJzR69/orders/"
    VALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}
    INVALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8G123"}

    def test_get(self, client):
        """
        Tests the GET method
        """
        # send with wrong api_secret for 401
        resp = client.get(self.RESOURCE_URL, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        # invalid url for 404
        resp = client.get(self.INVALID_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        # get with valid api_secret
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        # we dont want to post unnecessary orders to bitmex
        # _check_control_post_method("add-order", client, body, headers=self.VALID_API_SECRET)
        assert len(body["items"]) == 1
        for item in body["items"]:
            _check_control_get_method("self", client, item, headers=self.VALID_API_SECRET)
            assert "id" in item
            assert "price" in item
            assert "symbol" in item
            assert "side" in item
            assert "size" in item

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """
        valid = _get_order_json()

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid), headers=self.VALID_API_SECRET)
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid, headers=self.VALID_API_SECRET)
        assert resp.status_code == 201
        print(resp.headers["Location"])
        resp = client.get(resp.headers["Location"], headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        # print(body)
        assert body["price"] == 3837.5
        assert body["size"] == 20
        assert body["symbol"] == "XBTUSD"
        assert body["side"] == "Buy"
        # we cant really know the id beforehand because it is assigned by BitMEX
        assert "id" in body

        _check_control_get_method("self", client, body, headers=self.VALID_API_SECRET)
        _check_control_delete_method("delete", client, body, headers=self.VALID_API_SECRET)

        # remove side field for 400
        valid.pop("side")
        resp = client.post(self.RESOURCE_URL, json=valid, headers=self.VALID_API_SECRET)
        assert resp.status_code == 400


class TestOrder(object):
    RESOURCE_URL = "/accounts/79z47uUikMoPe2eADqfJzRBu/orders/00000000-0000-0000-0000-000000000000/"
    INVALID_URL = "/accounts/79z47uUikMoPe2eADqfJzR69/orders/10000000-0000-0000-0000-000000000001/"
    VALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}
    INVALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8G123"}

    def test_get(self, client):
        """
        Tests the get method, first checks for correct error responses, then
        does valid request and checks if the response data has all the required
        fields and the hypermedia controls work.
        """
        # send with wrong api_secret for 401
        resp = client.get(self.RESOURCE_URL, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        # invalid url for 404
        resp = client.get(self.INVALID_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        # get with valid api_secret
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)

        assert body["price"] == 3567.5
        assert body["size"] == 1
        assert body["symbol"] == "XBTUSD"
        assert body["side"] == "Buy"

        _check_control_get_method("self", client, body, headers=self.VALID_API_SECRET)
        _check_control_get_method("orders-all", client, body, headers=self.VALID_API_SECRET)
        _check_control_delete_method("delete", client, body, headers=self.VALID_API_SECRET)

    def test_delete(self, client):
        """
        Tests the delete method, first checks for correct error responses, then
        does valid request checks if the resource exist after the delete request
        """

        # Send with wrong api_secret for 401
        resp = client.delete(self.RESOURCE_URL, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        #  Send with right url and check after if the resource exists
        resp = client.delete(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        #  send with wrong url for 404
        resp = client.delete(self.INVALID_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404


class TestPriceAction(object):
    RESOURCE_URL = "/priceaction/"
    VALID_DATA = {"symbol": "XBTUSD"}
    INVALID_DATA = {}

    def test_get(self, client):
        """
        Tests get method and the controls that has been implemented.
        Checks that the wrong query parameter gives proper error response
        """
        # send get with valid query parameter
        resp = client.get(self.RESOURCE_URL, query_string=self.VALID_DATA)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_control_get_method("self", client, body)

        # send get with invalid query parameter for 400
        resp = client.get(self.RESOURCE_URL, query_string=self.INVALID_DATA)
        assert resp.status_code == 400


class TestPositions(object):
    RESOURCE_URL = "/accounts/79z47uUikMoPe2eADqfJzRBu/positions/"
    INVALID_URL = "/accounts/79z47uUikMoPe2eADqfJzRxx/positions/"
    VALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}
    INVALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8G123"}

    def test_get(self, client):
        """
        Tests the get method, first checks for correct error responses, then
        does valid request and checks if the response data has all the required
        fields and the hypermedia controls work. Because the positions are active positions
        in BitMEX test net, their amount can change and test assert might fail.
        """
        # send get with invalid api secret for 401
        resp = client.get(self.RESOURCE_URL, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        # invalid url for 404
        resp = client.get(self.INVALID_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        # get with valid api_secret
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        # Checks if we have three active positions in BitMEX test net like we should
        assert len(body["items"]) == 2
        _check_control_get_method("account", client, body, headers=self.VALID_API_SECRET)
        for item in body["items"]:
            _check_control_get_method("self", client, item, headers=self.VALID_API_SECRET)
            assert "symbol" in item
            assert "size" in item
            assert "leverage" in item
            assert "avgEntryPrice" in item
            assert "liquidationPrice" in item

class TestPosition(object):
    RESOURCE_URL = "/accounts/79z47uUikMoPe2eADqfJzRBu/positions/ADAM19/"
    INVALID_URL = "/accounts/79z47uUikMoPe2eADqfJzRxx/positions/asdf123/"
    VALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbjd"}
    INVALID_API_SECRET = {"api_secret": "j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8G123"}


    def test_get(self, client):
        """
        Tests the get method, first checks for correct error responses, then
        does valid request and checks if the response data has all the required
        fields and the hypermedia controls work.
        """

        resp = client.get(self.RESOURCE_URL, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        # invalid url for 404
        resp = client.get(self.INVALID_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        # get with valid api_secret
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_control_get_method("self", client, body, headers=self.VALID_API_SECRET)
        _check_control_get_method("positions-all", client, body, headers=self.VALID_API_SECRET)
        _check_control_patch_method("edit", client, body, headers=self.VALID_API_SECRET)

    def test_patch(self, client):
        """
        Tests the patch method, first checks for correct error responses
        Then checks the leverage value from the resource, sends valid PATCH
        request. Checks that status code is 204 and then checks that the
        leverage was correctly changed.
        """
        valid = _get_leverage_json()

        # test with wrong content type for 415
        resp = client.patch(self.RESOURCE_URL, data=json.dumps(valid), headers=self.VALID_API_SECRET)
        assert resp.status_code == 415

        # test with wrong url for 404
        resp = client.patch(self.INVALID_URL, json=valid, headers=self.VALID_API_SECRET)
        assert resp.status_code == 404

        # test with wrong api_secret for 401
        resp = client.patch(self.RESOURCE_URL, json=valid, headers=self.INVALID_API_SECRET)
        assert resp.status_code == 401

        # get wrong json for 400
        resp = client.patch(self.RESOURCE_URL, json=_get_order_json(), headers=self.VALID_API_SECRET)
        assert resp.status_code == 400


        # check that leverage is 1
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["leverage"] == 1
        # send patch and check if leverage is 2
        resp = client.patch(self.RESOURCE_URL, json=valid, headers=self.VALID_API_SECRET)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL, headers=self.VALID_API_SECRET)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["leverage"] == 2
