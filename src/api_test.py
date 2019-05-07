import pytest
import tempfile
import os
from app import app
from database import User, Orders, db
from sqlalchemy.engine import Engine
from sqlalchemy import event


"""
These tests are based on the api testing example found in lovelace

"""

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.config["TESTING"] = True
    db.init_app(app)

    with app.app_context():
        db.create_all()
        populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():
    """ Populates database with four users each with one order """
    with app.app_context():
        for i in range(1, 4):
            user=User(username="testuser-{}".format(i),
                      api_public="79z47uUikMoPe2eADqfJzRB{}".format(i),
                      api_secret="j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbj{}".format(i))

            order = Orders(order_id='00000000-0000-0000-0000-00000000000{}'.format(i),
                          order_size=1, order_side='Buy',
                          order_symbol="XBTUSD")

            user.orders.append(order)
            db.session.add(user)
        db.session.commit()

def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

def _check_control_post_method(ctrl, client, obj):
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
    resp = client.post(href, json=body)
    assert resp.status_code == 201

def _check_control_patch_method(ctrl, client, obj):
    """
    Checks a PATCH type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
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
    resp = client.patch(href, json=body)
    assert resp.status_code == 204

def _get_account_json():
    """ Creates account json object that is used in POST account test """
    pass

def _get_order_json():
    """ Creates order json object that is used in POST order test """
    pass

def _get_leverage_json():
    """ Creates leverage json object that is used in PATCH position test """
    pass


class TestAccounts(object):
    pass

class TestAccount(object):
    pass

class TestOrders(object):
    pass

class TestOrder(object):
    pass

class TestPriceAction(object):
    pass

class TestPositions(object):
    pass

class TestPosition(object):
    pass
