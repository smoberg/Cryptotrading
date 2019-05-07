import pytest
import tempfile
import os
import app
from database import User, Orders, db
from sqlalchemy.engine import Engine
from sqlalchemy import event


"""
These tests are based on the database testing example found in lovelace

"""

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def db_handle():
    db_fd, db_fname = tempfile.mkstemp()
    app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    app.app.config["TESTING"] = True
    app.app.config["DEBUG"] = False
    db.init_app(app.app)

    with app.app.app_context():
        db.create_all()

    yield db

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _get_user(number=1):
    """ Creates user model """
    return User(username="testuser-{}".format(number),
                api_public="79z47uUikMoPe2eADqfJzRB{}".format(number),
                api_secret="j9ey6Lk2xR6V-qJRfN-HqD2nfOGme0FnBddp1cxqK6k8Gbj{}".format(number))

def _get_order(number=1):
    """ Creates order model """
    return Orders(order_id='00000000-0000-0000-0000-00000000000{}'.format(number),
                  order_price=3567.5, order_size=1, order_side='Buy',
                  order_symbol="XBTUSD")

def test_create_instances(db_handle):
    """
    Tests that we can create one instance of each model and save them to the
    database using valid values for all columns. After creation, test that
    everything can be found from database, and that all relationships have been
    saved correctly.
    """

    # Make everything, add order to user's order relationship
    with app.app.app_context():
        user = _get_user()
        order = _get_order()
        user.orders.append(order)
        db_handle.session.add(user)
        db_handle.session.add(order)
        db.session.commit()
        # Check that everything exists
        assert User.query.count() == 1
        assert Orders.query.count() == 1
        db_user = User.query.first()
        db_order = Orders.query.first()
        # Relationship check
        assert db_order in db_user.orders
        assert db_user == db_order.user

def test_order_ondelete_user(db_handle):
    """
    Tests that foreign key in order is set to null if user is deleted.
    """
    with app.app.app_context():
        user = _get_user()
        order = _get_order()
        user.orders.append(order)
        db_handle.session.add(order)
        db_handle.session.commit()
        db_handle.session.delete(user)
        db_handle.session.commit()
        assert order.user_id is None

def test_order_onupdate_user(db_handle):
    """
    Tests that foreign key in order is cascaded properly if user.id is modified
    """
    with app.app.app_context():
        user = _get_user()
        order = _get_order()
        user.orders.append(order)
        db_handle.session.add(user)
        db_handle.session.add(order)
        db.session.commit()
        db_user = User.query.first()
        db_user.id = 73
        db.session.commit()
        db_order = Orders.query.first()
        assert db_order.user_id == 73
