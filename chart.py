import altair as alt
import datetime
import pandas as pd

import categories
from database import Listing
import model

def prepare_chart_data(df, item, aggregate=True):
    df = df[df['item_id'].apply(lambda x : not categories.by_id(x).disabled)]
    def cat_selector(x):
        cat = categories.by_id(x)
        return cat.category() == item or cat == item

    if item == categories.buy_sell:
        df['cat_id'] = df['item_id'].apply(lambda x : categories.by_id(x).category().id)
        if aggregate:
            df2 = df[['cat_id', 'post_date', 'count', 'logsum']].groupby(['cat_id', 'post_date']).sum().reset_index()
        else:
            df2 = df.copy()
    else:
        df['cat_id'] = df['item_id']
        df2 = df[df['cat_id'].apply(cat_selector)].copy()

    df2['date'] = df2['post_date'].apply(lambda x : x.isoformat())
    df2['item'] = df2['cat_id'].apply(lambda x : categories.by_id(x).string)
    return df2


def histogram(item):
    df = prepare_chart_data(Listing.item_date_count_log(), item)
    data = df[['item', 'date', 'count']]
    chart = alt.Chart(data).mark_bar().encode(
        x='date:T',
        y='count:Q',
        color='item'
    ).properties(width=600, height=400)
    chart.save('static/charts/hist-chart-' + item.name + '.json')


def prices(item):
    df = prepare_chart_data(Listing.item_date_count_log(), item)
    if len(df.index) == 0:
        return None
    df_sum = df[['date', 'count', 'logsum']].groupby(['date']).sum().reset_index()
    f = lambda row : 0 if row['count'] == 0 else row['logsum']/row['count']
    df['log_price'] = df.apply(f, axis=1)
    df_sum['log_price'] = df_sum.apply(f, axis=1)

    data = df[['item', 'date', 'log_price']]
    data_sum = df_sum[['date', 'log_price']]

    chart = rolling_mean_chart(data, data_sum, 'log_price')

    try:
        os.makedirs('static/charts')
    except FileExistsError:
        pass
    chart.save('static/charts/price-chart-' + item.name + '.json')


def residuals(item):
    if item == categories.buy_sell:
        cats = categories.categories()
    else:
        cats = [item.category()]
    Xs = []
    for cat in cats:
        est = model.CatModel(cat)
        est.load()
        (X,y) = model.prepare_cat_data(cat)
        if X is None:
            continue
        X['residual'] = y - est.predict(X)
        Xs.append(prepare_chart_data(X.copy(), item, aggregate=False))
    X_prep = pd.concat(Xs)
    data = X_prep[['item', 'date', 'residual']].groupby(['item', 'date']).mean().reset_index()
    data_sum = X_prep[['date', 'residual']].groupby('date').mean().reset_index()

    chart = rolling_mean_chart(data, data_sum, 'residual')

    try:
        os.makedirs('static/charts')
    except FileExistsError:
        pass
    chart.save('static/charts/residual-chart-' + item.name + '.json')




def rolling_mean_chart(data, data_sum, y):
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
    try:
        os.makedirs('static/charts')
    except FileExistsError:
        pass
    return chart.properties(width=600, height=400)
