from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
import pandas as pd
import categories
import sys
import scrape as sc

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)

class Listing(db.Model):
    __tablename__ = 'listings'
    id          = db.Column(db.Integer, primary_key=True)
    url         = db.Column(db.Text)
    price       = db.Column(db.Integer)
    title       = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    location    = db.Column(db.Text)
    post_date   = db.Column(db.Date, default=db.func.current_date())
    retreived   = db.Column(db.DateTime, default=db.func.current_timestamp())
    item_id     = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item        = db.relationship('Item', backref=db.backref('listings', lazy=True))

    # Retreive new listings from kijiji and put in the database
    # If items is None, get all new listings, else only for the items in the list.
    def update(items=None):
        if items is None:
            items = categories.item_dict.keys()
        for item in items:
            try:
                i = Item.query.filter(Item.name == item).one()
            except NoResultFound:
                i = Item(item)
                db.session.add(i)
                db.session.commit()
            start_date = i.update_time
            if start_date is not None:
                start_date = start_date.date()
            df = sc.scrape(item, start_date=start_date)
            Listing.from_df(df)
            i.update_time = db.func.current_timestamp()
            db.session.commit()

    # Add contents of a database into the listings table
    def from_df(df):
        if df is not None:
            #df.to_sql(name='listings', if_exists='append', con=db.engine)
            for index,row in df.iterrows():
                l = Listing(id=index, **row)
                db.session.merge(l)
            db.session.commit()

    # Create dataframe for item listings in table
    def to_df(item):
        item_id = categories.item_dict[item]
        q = Listing.query.filter(Listing.item_id == item_id)
        df = pd.read_sql(q.statement, db.session.bind)
        return df

    def __repr__(self):
        return f'Listing: {self.id}'


class Item(db.Model):
    __tablename__ = 'items'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.Text, nullable=False)
    category    = db.Column(db.Text, nullable=False)
    update_time = db.Column(db.DateTime)

    def __init__(self, item):
        self.id = categories.item_dict[item]
        self.name = item
        self.category = categories.item_category[item]

    def __repr__(self):
        return f'Item: {self.id}, {self.name}'