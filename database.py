from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
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
    #item        = db.Column(db.Integer)
    url         = db.Column(db.Text)
    price       = db.Column(db.Integer)
    title       = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    location    = db.Column(db.Text)
    post_date   = db.Column(db.Date, default=db.func.current_date())
    #retreived   = db.Column(db.DateTime, default=db.func.current_timestamp())

    item_id     = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item        = db.relationship('Item', backref=db.backref('listings', lazy=True))

    update_id   = db.Column(db.Integer, db.ForeignKey('updates.id'))
    update      = db.relationship('Update', backref=db.backref('listings', lazy=True))

    def __repr__(self):
        return f'Listing: {self.id}'

class Item(db.Model):
    __tablename__ = 'items'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.Text, nullable=False)
    category    = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Item: {self.id}, {self.name}'

class Update(db.Model):
    __tablename__ = 'updates'
    id          = db.Column(db.Integer, primary_key=True)
    date        = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'Update: {self.date}'

# Add contents of a database into the listings table
def df_to_db(df, update_id=None):
    if df is None:
        return None
    #df.to_sql(name='listings', if_exists='append', con=db.engine)
    n = 0
    m = 0
    for index,row in df.iterrows():
        l = Listing(id=index, **row, update_id=update_id)
        db.session.merge(l)
    db.session.commit()
    return None


def db_to_df(item, update_id=None):
    item_id = categories.item_dict[item]
    q = Listing.query.filter(Listing.item_id == item_id)
    if update_id is not None:
        q = q.filter(Listing.update_id == update_id)
    df = pd.read_sql(q.statement, db.session.bind)
    return df


def update(items=None):
    start_date = None
    n = Update.query.count()
    if n > 0:
        start_date = Update.query.order_by(Update.id.desc()).first().date.date()
    u = Update()
    if items is None:
        items = categories.item_dict.keys()
    for item in items:
        df = sc.scrape(item, start_date=start_date)
        df_to_db(df, update_id=u.id)
    db.session.add(u)
    db.session.commit()
