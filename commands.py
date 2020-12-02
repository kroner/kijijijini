import click
import categories
import scrape as sc
import model
import database
from database import db, Listing, Item
import sys

# Creates database table
@click.argument("table")
def create(table):
    if table == 'items':
        Item.__table__.create(db.engine)
        #for item in categories.item_dict:
        #    database.add_item(item)
    if table == 'listings':
        Listing.__table__.create(db.engine)

# Cleans database
@click.argument("table")
def drop(table):
    if table == 'items':
        Item.__table__.drop(db.engine)
    if table == 'listings':
        Listing.__table__.drop(db.engine)

# Add listings from csv files to the database
def read_csvs():
    for item in categories.item_dict:
        Item.get(item)
    #for item in ['art-collectables']:
        try:
            df = sc.csv_to_df(item)
            Listing.from_df(df)
        except FileNotFoundError:
            pass
        print(item, file=sys.stdout)

# Scrape new listings from kijiji and add them to the database
@click.argument("x")
def update(x):
    if x == 'database':
        Listing.update()
    if x == 'model':
        model.train_all()


def init_app(app):
    commands = [create, drop, read_csvs, update]
    for command in commands:
        app.cli.add_command(app.cli.command()(command))
