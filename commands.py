import click
import categories
import scrape as sc
import model
import database
from database import db, Listing, Item, Update
import sys

# Creates database table
@click.argument("table")
def create(table):
    if table == 'items':
        Item.__table__.create(db.engine)
        for item in categories.item_dict:
            i = Item(id=categories.item_dict[item], name=item, category=categories.item_category[item])
            db.session.add(i)
        db.session.commit()
    if table == 'listings':
        Listing.__table__.create(db.engine)
    if table == 'updates':
        Update.__table__.create(db.engine)

# Cleans database
@click.argument("table")
def drop(table):
    if table == 'items':
        Item.__table__.drop(db.engine)
    if table == 'listings':
        Listing.__table__.drop(db.engine)
    if table == 'updates':
        Update.__table__.drop(db.engine)

# Add listings from csv files to the database
def read_csvs():
    for item in categories.item_dict:
    #for item in ['art-collectables']:
        df = sc.csv_to_df(item)
        database.df_to_db(df)

# Scrape new listings from kijiji and add them to the database
@click.argument("x")
def update(x):
    if x == 'database':
        database.update()
    if x == 'model':
        model.update()


def init_app(app):
    commands = [create, drop, read_csvs, update]
    for command in commands:
        app.cli.add_command(app.cli.command()(command))
