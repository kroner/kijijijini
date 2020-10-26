import sys
import pandas as pd
import math
import collections as cln
import heapq
import dill
from datetime import datetime
from sklearn import base
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
from sklearn import compose
from sklearn import metrics
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
import scrape

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
        return [parse(row['text']) for row in X]

'''
def top_words(s, limit=None, word_list=None, sorted=True):
	if word_list is None:
		word_counts = cln.defaultdict(int)
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
'''

class WordEncoder(base.BaseEstimator, base.TransformerMixin):

	def __init__(self, limit=None, word_list=None, count=False):
		self.limit = limit
		self.word_list = word_list
		self.count = count

	def fit(self, X, y=None):
		data = X.iloc[:,0].array
		top = [('hello',1)]#top_words(data, limit=self.limit, sorted=False)
		#print(top[:50])
		self.word_list = [t[0] for t in top]
		return self

	def transform(self, X):
		data = X.iloc[:,0].array
		Xt = list()
		for text in data:
			cs = [('hello', 1)]#top_words([text], word_list=self.word_list, sorted=False)
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


# read in all the data for a category and return X and y
def prepare_cat_data(cat):
	items = categories.categories[cat]
	price_func = lambda x : math.log(x+25)
	#price_func = lambda x : math.sqrt(x)
	dfs = []
	for (item, _) in items:
		df = scrape.read_in_item_data(item)
		df['item'] = item
		dfs.append(df)
	data = pd.concat(dfs)
	X = data.drop('price', axis=1)
	X = X.drop(X.columns[0], axis=1)
	y = data['price'].apply(price_func)
	return (X,y)


def train_model(cat):
	title_lim = 400
	desc_lim = 550
	print('training... ', end='')
	(X,y) = prepare_cat_data(cat)
	colt = compose.ColumnTransformer([
		('item', OneHotEncoder(), ['item']),
		#('const', 'passthrough', ['const']),
		('title', WordEncoder(limit=title_lim), ['title']),
		('description', WordEncoder(limit=desc_lim), ['description'])])
	est = Pipeline([
        ('transform', colt),
        ('est', LinearRegression())
    ])
	est.fit(X,y)
	model_path = open('est-' + cat + '.pkd', 'wb')
	dill.dump(est, model_path)
	model_path.close()
	print('done')
	y_pred = est.predict(X)
	print(len(X.index))
	print(metrics.r2_score(y,y_pred))
	return est


def load_model(cat):
	model_path = open('est-' + cat + '.pkd', 'rb')
	est = dill.load(model_path)
	model_path.close()
	return est


# predict the price for a dict with 'title', 'description', 'item'
def predict_price(Xdict):
	cat = categories.item_category[Xdict['item']]
	sample_X = pd.DataFrame({
		'url':[''],
		'title':[Xdict['title']],
		'distance':[''],
		'description':[Xdict['description']],
		'location':[''],
		'time_offset':[datetime.now()],
		'retreived':[datetime.now()],
		'item':[Xdict['item']]
		})
	try:
		est = load_model(cat)
	except FileNotFoundError:
		est = train_model(cat)
	sample_y = est.predict(sample_X)[0]
	price = math.exp(sample_y)-25
	return price



if __name__ == '__main__':
	train_model('furniture')
	'''
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
	title = '18" tall metal bed frame'
	desc = 'Selling an 18" tall metal bed frame. Comes apart at corners for easy assembly. Great for condo as the height is perfect for under bed storage bins or luggate. Frame is in near perfect condition.  Comes with wooden slats.'
	sample_X = {'title':title, 'description':desc, 'item':'bed-mattress'}
	print(sample_X)
	print(predict_price(sample_X))
