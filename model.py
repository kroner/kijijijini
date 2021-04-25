import sys
import string
import pandas as pd
import math
from collections import defaultdict
import heapq
import dill
import os
import datetime
import boto3
from sklearn import base
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import r2_score
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.utils import shuffle
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer

import categories
from database import Listing

BUCKET_NAME = 'kijijijini'
SAMPLE_SIZE = 100000
MODELS_PATH = 'models/'


class ModelTransformer(base.BaseEstimator, base.TransformerMixin):
    def __init__(self, est):
        self.est = est
    def fit(self, X, y):
        self.est.fit(X,y)
        return self
    def transform(self, X):
        y = self.est.predict(X)
        return [[a] for a in y]

def parse(text):
            text = text.translate(str.maketrans('', '', string.punctuation))
            #return [word.lower() for word in text.split()]
            return text.lower()

class ColumnSelectTransformer(base.BaseEstimator, base.TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return X.iloc[:, 0].tolist()


def top_words(s, limit=None, word_list=None, sorted=True):
	if word_list is None:
		word_counts = defaultdict(int)
	else:
		word_counts = dict([(w,0) for w in word_list])
	for text in s:
		words = [word.lower() for word in text.split()]
		for word in words:
			if word_list is None or word in word_counts:
				word_counts[word] += 1
	top = [pair for pair in word_counts.items() if pair[0][0] != '$' and pair[0] != 'free']
	if limit is None and sorted:
		top.sort(key=lambda w : w[1])
	if limit is not None:
		limit = min(limit, len(word_counts))
		top = heapq.nlargest(limit, top, key=lambda w : w[1])
	return top


class WordEncoder(base.BaseEstimator, base.TransformerMixin):
	import pandas as pd

	def __init__(self, limit=None, word_list=None, count=False):
		self.limit = limit
		self.word_list = word_list
		self.count = count

	def fit(self, X, y=None):
		data = X.iloc[:,0].array
		top = top_words(data, limit=self.limit, sorted=False)
		#print(top[:50])
		self.word_list = [t[0] for t in top]
		return self

	def transform(self, X):
		data = X.iloc[:,0].array
		Xt = list()
		for text in data:
			cs = top_words([text], word_list=self.word_list, sorted=False)
			if self.count:
				cs = [c[1] for c in cs]
			else:
				cs = [int(c[1] > 0) for c in cs]
			Xt.append(cs)
		return pd.DataFrame(Xt)


def cross_validate(X,y,est):
	X_random_order, y_random_order = shuffle(X, y)
	cv_test_error = -cross_val_score(
            est,
            X_random_order,
            y_random_order,
            cv=5,  # number of folds
            scoring='neg_root_mean_squared_error')
	return cv_test_error.mean()


def print_nice(coefs,file=sys.stdout):
	for pair in coefs:
		string = "'" + pair[0] + "'"
		value = (math.exp(pair[1]) - 1)
		#print(pair[1])
		print('{:15s} {:-4.0%}'.format(string,value),file=file)
	return None


def make_model_path(s):
    try:
        os.makedirs(MODELS_PATH)
    except FileExistsError:
        pass
    return MODELS_PATH + s

# read in all the data for a category and return X and y
# for large data sets, sample down
def prepare_cat_data(cat, sample=None):
    price_func = lambda x : math.log(x+25)
    data = Listing.to_df(cat, children=True, sample=sample)
    if len(data.index) == 0:
        return (None, None)
    if len(data.index) > SAMPLE_SIZE:
        data = data.sample(n=SAMPLE_SIZE)
    X = data.drop('price', axis=1)
    X = X.drop(X.columns[0], axis=1)
    y = data['price'].apply(price_func)
    return (X,y)

class CatModel():
    def __init__(self, cat):
        self.cat = cat
        (self.X, self.y) = (None, None)
        '''
        title_lim = 400
        desc_lim = 550
        colt = ColumnTransformer([
            ('item', OneHotEncoder(), ['item']),
            #('const', 'passthrough', ['const']),
            ('title', WordEncoder(limit=title_lim), ['title']),
            ('description', WordEncoder(limit=desc_lim), ['description'])
            ])
        est = Pipeline([
            ('transform', colt),
            ('est', LinearRegression())
            ])
        '''
        tfidf_title = Pipeline([
            ('cst', ColumnSelectTransformer()),
            ('tfidf', TfidfVectorizer()),
            ])
        tfidf_desc = Pipeline([
            ('cst', ColumnSelectTransformer()),
            ('tfidf', TfidfVectorizer()),
            ])
        colt = ColumnTransformer([
            ('item', OneHotEncoder(), ['item_id']),
            ('title', tfidf_title, ['title']),
            ('description', tfidf_desc, ['description'])
            ])
        self.est = Pipeline([
            ('trans', colt),
            ('est', SGDRegressor())
            ])

    def load(self):
        model_path = make_model_path('est-' + self.cat.name + '.pkd')

        s3 = boto3.client('s3')
        with open(model_path, 'wb') as model_file:
            s3.download_fileobj(BUCKET_NAME, model_path, model_file)
        with open(model_path, 'rb') as model_file:
            self.est = dill.load(model_file)
        '''
        try:
            with open(model_path, 'rb') as model_file:
                self.est = dill.load(model_file)
            return None
        except FileNotFoundError:
            pass

        try:
            s3 = boto3.client('s3')
            with open(model_path, 'wb') as model_file:
                s3.download_fileobj(BUCKET_NAME, model_path, model_file)
            with open(model_path, 'rb') as model_file:
                self.est = dill.load(model_file)
            return None
        except:
            pass
        
        self.fit()
        '''


    def save(self):
        model_path = make_model_path('est-' + self.cat.name + '.pkd')
        with open(model_path, 'wb') as model_file:
            dill.dump(self.est, model_file)

        s3 = boto3.client('s3')
        with open(model_path, "rb") as model_file:
            s3.upload_fileobj(model_file, BUCKET_NAME, model_path)


    def fit(self, print_r2=False):
        (X, y) = prepare_cat_data(self.cat)
        print(self.cat.name, ': training... ', end='', file=sys.stdout)
        if X is None:
            print('no data', file=sys.stdout)
            return None
        self.est.fit(X, y)
        self.save()
        print('done', file=sys.stdout)
        print(' ', len(X.index), file=sys.stdout)
        if print_r2:
            y_pred = self.est.predict(X)
            print(r2_score(y, y_pred))

    def predict(self, X):
        return self.est.predict(X)



# predict the price for a dict with 'title', 'description', 'item'
def predict_price(Xdict):
    if 'item' in Xdict:
        item = categories.by_name(Xdict['item'])
    else:
        item = categories.by_id(Xdict['item_id'])
    sample_X = pd.DataFrame({
        'url' : [''],
        'title' : [Xdict['title']],
        'description' : [Xdict['description']],
        'location' : [''],
        'post_date' : [datetime.date.today()],
        'retreived' : [datetime.datetime.now()],
        'item_id' : [item.id]
        })
    est = CatModel(item.category())
    est.load()
    sample_y = est.predict(sample_X)[0]
    price = math.exp(sample_y)-25
    return price

'''
def histogram_data(item):
	df = Listing.to_df(item)
	df['post_str'] = df['post_date'].apply(lambda x : x.isoformat())
	if item == categories.buy_sell:
		df['item'] = df['item_id'].apply(lambda x : categories.by_id(x).category().name)
	else:
		df['item'] = df['item_id'].apply(lambda x : categories.by_id(x).name)
	data = df[['item', 'post_str']]

def some_stupid_test_stuff(est):
	coefs = pipe.named_steps.est.coef_
	#print(coefs[:50])
	col_trans = pipe.named_steps.transform.named_transformers_
	tword_list = col_trans['title'].word_list
	dword_list = col_trans['description'].word_list
	title_coefs = list(zip(tword_list, coefs[-desc_lim-title_lim: -desc_lim]))
	desc_coefs = list(zip(dword_list, coefs[-desc_lim:]))
	#title_sorted = sorted(title_coefs,key=lambda x:-abs(x[1]))
	#desc_sorted = sorted(desc_coefs,key=lambda x:-abs(x[1]))
	out_file = open('out.txt', 'w')
	print_nice(sorted(title_coefs,key=lambda x:-x[1]),file=out_file)
	print('',file=out_file)
	print_nice(sorted(title_coefs,key=lambda x: x[1]),file=out_file)
	print('',file=out_file)
	print_nice(sorted(desc_coefs,key=lambda x:-x[1]),file=out_file)
	print('',file=out_file)
	print_nice(sorted(desc_coefs,key=lambda x: x[1]),file=out_file)
	out_file.close()
	#print_nice(title_coefs[:50])
	#print(cross_validate(X,y,pipe))
	print(X)
'''

if __name__ == '__main__':
    est = CatModel(categories.by_name('furniture'))
    est.load()
    title = '18" tall metal bed frame'
    desc = 'Selling an 18" tall metal bed frame. Comes apart at corners for easy assembly. Great for condo as the height is perfect for under bed storage bins or luggate. Frame is in near perfect condition.  Comes with wooden slats.'
    sample_X = {'title':title, 'description':desc, 'item':'bed-mattress'}
    print(sample_X)
    print(predict_price(sample_X))
