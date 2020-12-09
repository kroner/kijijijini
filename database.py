from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, literal
from sqlalchemy.types import Numeric
from sqlalchemy.orm.exc import NoResultFound
import pandas as pd
import sys
import os
import datetime


OUTLIER = 8000

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)

# The main table of all listings
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

    # Add contents of a database into the listings table
    def from_df(df):
        if df is not None:
            #df.to_sql(name='listings', if_exists='append', con=db.engine)
            for index,row in df.iterrows():
                l = Listing(id=index, **row)
                db.session.merge(l)
            db.session.commit()

    # Create dataframe for item listings in table
    def to_df(item, children=True, disabled=False, sample=None):
        dfs = []
        #if os.environ.get('FLASK_ENV') != 'development' and sample is not None:
        #    n = Listing.query.filter(Listing.item_id == item.id).filter(Listing.price < literal(OUTLIER)).count()
        #    p = min(sample/n, 1)
        #    sql = f'''
        #        SELECT *
        #        FROM listings TABLESAMPLE BERNOULLI {p}
        #        WHERE item_id = {item.id} AND price < {OUTLIER};
        #        '''
        #else:
        #    sql = f'''
        #        SELECT *
        #        FROM listings
        #        WHERE item_id = {item.id} AND price < {OUTLIER};
        #        '''
        #dfs.append(pd.read_sql(sql, db.session.bind, parse_dates=['post_date']))
        q = Listing.query.filter(Listing.item_id == item.id).filter(Listing.price < literal(OUTLIER))
        dfs.append(pd.read_sql(q.statement, db.session.bind))
        if children:
            for child in item.children():
                if child != item:
                    dfs.append(Listing.to_df(child, children=True, disabled=disabled))
        return pd.concat(dfs)

    # return summary statistics of #listings for each (item, date) pair
    def item_date_count_log():
        cols = [
            Listing.item_id,
            Listing.post_date,
            func.count().label('count'),
            func.sum(Listing.price + literal(25.0)).label('logsum'),
            ]
        #if os.environ.get('FLASK_ENV') != 'development':
        #    cols[-1] = func.sum(func.log(Listing.price + literal(25.0))).label('logsum')
        q = Listing.query.filter(Listing.price < literal(OUTLIER)) \
            .with_entities(
                Listing.item_id,
                Listing.post_date,
                func.count().label('count'),
                func.sum(Listing.price + literal(25.0)).label('logsum'),
            ).group_by(Listing.item_id, Listing.post_date)
        return pd.read_sql(q.statement, db.session.bind)


    def __repr__(self):
        return f'Listing: {self.id}'



# A table of item types and when they were last scraped
class Item(db.Model):
    __tablename__ = 'items'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.Text, nullable=False)
    category    = db.Column(db.Text, nullable=False)
    update_time = db.Column(db.DateTime)

    def __init__(self, item):
        self.id = item.id
        self.name = item.name
        self.category = item.category().name

    # Get database row for an item
    def get(item):
        if Item.query.filter(Item.id == item.id).count() != 1:
            i = Item(item)
            db.session.add(i)
            db.session.commit()
        return Item.query.filter(Item.id == item.id).one()

    # The date of the last update
    def last_date(self):
        ld = self.update_time
        if ld is not None:
            ld = ld.date()
        return ld

    # put listings from df into the database and update the update_time
    def update(self, df):
        Listing.from_df(df)
        self.update_time = db.func.current_timestamp()
        db.session.commit()

    # If item hasn't been scraped recently
    def is_old(self, delta):
        update_time = self.update_time
        return update_time is None or datetime.datetime.now() - update_time >= delta

    def __repr__(self):
        return f'Item: {self.id}, {self.name}'
