from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import click
from flask.cli import with_appcontext
from cryptotrading_api import db


class Orders(db.Model):
    API_key = db.Column(db.String(24), nullable=False)
    Order_id = db.Column(db.String(36), nullable=False, primary_key=True)
    Order_size = db.Column(db.Integer, nullable=False)
    Order_side = db.Column(db.String(4), nullable=False)
    Order_symbol = db.Column(db.String(10), nullable=False)

@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
