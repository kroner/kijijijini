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
        #for item in categories.all_items():
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
    for item in categories.items():
        Item.get(item)
    #for item in ['art-collectables']:
        try:
            df = sc.csv_to_df(item)
            Listing.from_df(df)
        except FileNotFoundError:
            pass
        print(item, file=sys.stdout)

# Scrape new listings from kijiji and add them to the database
@click.argument("cat")
def update(cat):
    if cat == 'all':
        items = categories.items()
    else:
        items = categories.by_name(cat).active_children()
    for item in items:
        n0 = Listing.query.filter(Listing.item_id == item.id).count()
        Listing.update(item)
        n1 = Listing.query.filter(Listing.item_id == item.id).count()
        print('New listings:', n1 - n0, file=sys.stdout)

# Retrain the models
@click.argument("cat")
def train(cat):
    if cat == 'all':
        cats = categories.categories()
    else:
        cats = [categories.by_name(cat)]
    for cat in cats:
        model.train(cat)


def init_app(app):
    commands = [create, drop, update, train]
    for command in commands:
        app.cli.add_command(app.cli.command()(command))
