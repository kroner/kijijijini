import click
import datetime
import sys

import categories
import scrape as sc
import model
import chart as ch
from database import db, Listing, Item

OLD = 20
SAMPLE_SIZE = 30000

# Creates database table
@click.argument("table")
def create(table):
    if table == 'items':
        Item.__table__.create(db.engine)
    if table == 'listings':
        Listing.__table__.create(db.engine)

# Drop database table
# CAUTION!
@click.argument("table")
def drop(table):
    if table == 'items':
        Item.__table__.drop(db.engine)
    if table == 'listings':
        Listing.__table__.drop(db.engine)

# Add listings from csv files to the database
# This shouldn't be needed anymore
def read_csvs():
    for item in categories.items():
    #for item in [categoties.by_name('art-collectibles')]:
        Item.get(item)
        try:
            df = sc.csv_to_df(item)
            Listing.from_df(df)
        except FileNotFoundError:
            pass
        print(item.name, file=sys.stdout)

# Scrape new listings from kijiji and add them to the database
@click.argument("cat")
def scrape(cat):
    delta = datetime.timedelta(hours=OLD) # interval for deciding if results are old
    if cat == 'all' or cat == 'all-old':
        items = categories.items(disabled=True)
    else:
        items = categories.by_name(cat).children(disabled=True)
    for item in items:
        if cat == 'all-old':
            if not Item.get(item).is_old(delta):
                continue
        n0 = Listing.query.filter(Listing.item_id == item.id).count()
        i = Item.get(item)
        df = sc.scrape(item, start_date=i.last_date())
        i.update(df)
        n1 = Listing.query.filter(Listing.item_id == item.id).count()
        print(f' new listings: {n1 - n0} ({n1})', file=sys.stdout)
        
    train('all')

# Retrain the models
@click.argument('cat')
def train(cat):
    if cat == 'all':
        cats = categories.categories()
    else:
        cats = [categories.by_name(cat)]
    for cat in cats:
        est = model.CatModel(cat)
        est.fit(print_r2=True)


def init_app(app):
    commands = [
        create,
        #drop,
        scrape,
        train,
        ]
    for command in commands:
        app.cli.add_command(app.cli.command()(command))
