import altair as alt
import datetime
import os
import pandas as pd

import categories
from database import Listing
import model

def prepare_chart_data(df, aggregate=True):
    df['date'] = df['post_date'].apply(lambda x : x.isoformat())
    df['cat_id'] = df['item_id'].apply(lambda x : categories.by_id(x).category().id)
    df_items = df[['item_id', 'date', 'count', 'logsum']].groupby(['item_id', 'date']).sum().reset_index()
    df_cats = df[['cat_id', 'date', 'count', 'logsum']].groupby(['cat_id', 'date']).sum().reset_index()
    df_all = df[['date', 'count', 'logsum']].groupby(['date']).sum().reset_index()

    df_items['cat'] = df_items['item_id'].apply(lambda x : categories.by_id(x).category().string)
    df_items['item'] = df_items['item_id'].apply(lambda x : categories.by_id(x).string)
    df_items['price'] = df_items['logsum']/df_items['count']

    df_cats['cat'] = categories.buy_sell.string
    df_cats['item'] = df_cats['cat_id'].apply(lambda x : categories.by_id(x).string)
    df_cats['price'] = df_cats['logsum']/df_cats['count']

    df_all['cat'] = categories.buy_sell.string
    df_all['item'] = categories.buy_sell.string
    df_all['price'] = df_cats['logsum']/df_cats['count']
    return (df_items, df_cats, df_all)


def histogram():
    (df_items, df_cats, df_all) = prepare_chart_data(Listing.item_date_count_log())
    data = df_cats[['item', 'date', 'count']]
    make_hist(data, categories.buy_sell)
    for cat in categories.categories():
        data = df_items[df_items['cat'] == cat.string][['item', 'date', 'count']]
        make_hist(data, cat)
    for item in categories.items():
        data = df_items[df_items['item_id'] == item.id][['item', 'date', 'count']]
        make_hist(data, item)

def make_hist(data, item):
    chart = alt.Chart(data).mark_bar().encode(
        x='date:T',
        y='count:Q',
        color='item'
    ).properties(width=600, height=400)

    try:
        os.makedirs('static/charts', exist_ok=True)
    except FileExistsError:
        pass
    chart.save(f'static/charts/hist-chart-{item.name}.json')

'''
def residuals(sample=None):
    if item == categories.buy_sell:
        cats = categories.categories()
    else:
        cats = [item.category()]
    Xs = []
    for cat in cats:
        est = model.CatModel(cat)
        est.load()
        (X,y) = model.prepare_cat_data(cat, sample=sample)
        if X is None:
            continue
        X['residual'] = y - est.predict(X)
        Xs.append(prepare_chart_data(X.copy(), aggregate=False))
    if not Xs:
        return None
    X_prep = pd.concat(Xs)
    data = X_prep[['item', 'date', 'residual']].groupby(['item', 'date']).mean().reset_index()
    data_sum = X_prep[['date', 'residual']].groupby('date').mean().reset_index()

    chart = rolling_mean_chart(data, data_sum, 'residual')

    try:
        os.makedirs('static/charts', exist_ok=True)
    except FileExistsError:
        pass
    chart.save('static/charts/residual-chart-' + item.name + '.json')
'''

def prices():
    (df_items, df_cats, df_all) = prepare_chart_data(Listing.item_date_count_log())
    print(categories.buy_sell.name + ' charts...', end='')
    data = df_cats[['item', 'date', 'price']]
    data_sum = df_all[['item', 'date', 'price']]
    rolling_mean_chart(data, data_sum, 'price', categories.buy_sell)
    print(' done')
    make_hist(data, categories.buy_sell)
    for cat in categories.categories():
        print(cat.name + ' charts...', end='')
        data = df_items[df_items['cat'] == cat.string][['item', 'date', 'price']]
        data_sum = df_cats[df_items['item'] == cat.string][['item', 'date', 'price']]
        rolling_mean_chart(data, data_sum, 'price', cat)
        print(' done')
    for item in categories.items():
        print(item.name + ' charts...', end='')
        data = df_items[df_items['item'] == item.string][['item', 'date', 'price']]
        rolling_mean_chart(data, data, 'price', item)
        print(' done')



def rolling_mean_chart(data, data_sum, y, item):
    item_chart = alt.Chart(data).mark_line().transform_window(
        rolling_mean='mean(' + y + ')',
        frame=[-4, 3]
    ).encode(
        x='date:T',
        y='rolling_mean:Q',
        color='item',
    )

    chart = alt.Chart(data_sum).mark_line(size=5, color='black').transform_window(
        rolling_mean='mean(' + y + ')',
        frame=[-4, 3]
    ).encode(
        x='date:T',
        y='rolling_mean:Q',
    )

    if len(data.index) != len(data_sum.index):
        chart = item_chart + chart
    chart = chart.properties(width=600, height=400)

    try:
        os.makedirs('static/charts', exist_ok=True)
    except FileExistsError:
        pass
    chart.save(f'static/charts/{y}-chart-{item.name}.json')
