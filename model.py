import sys
import pandas as pd
import math
import collections as cln
import heapq
from datetime import datetime
from sklearn import base
from sklearn.linear_model import LinearRegression
from sklearn import compose
from sklearn import metrics
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
from sklearn.utils import shuffle
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import OneHotEncoder

import categories

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


class WordEncoder(base.BaseEstimator, base.TransformerMixin):
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
		data = data = X.iloc[:,0].array
		Xt = []
		for text in data:
			cs = top_words([text], word_list=self.word_list, sorted=False)
			if self.count:
				cs = [c[1] for c in cs]
			else:
				cs = [int(c[1] > 0) for c in cs]
			Xt.append(cs)
		return pd.DataFrame(Xt)


def read_in_data(item):
	save_path = '/home/robert/Documents/DataSets/kijiji_data/'
	file_path = save_path + 'kdat-' + item + '.csv'
	data_file = open(file_path, 'r')
	df = pd.read_csv(data_file)
	data_file.close()
	return df

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


if __name__ == '__main__':
	items = ['chair-recliner',
			 'bed-mattress',
			 'couch-futon',
			 'dining-table-set',
			 'coffee-table-ottoman',
			 'hutch-display-cabinet',
			 'dresser-wardrobe',
			 'furniture-other-table',
			 'bookcase-shelves',
			 'other-furniture',
			 'buy-sell-desks',
			 'tv-table-entertainment-unit']
	price_func = lambda x : math.log(x+25)
	title_lim = 400
	desc_lim = 550
	#price_func = lambda x : math.sqrt(x)
	dfs = []
	for item in items:
		df = read_in_data(item)
		df['category'] = item
		dfs.append(df)
	data = pd.concat(dfs)
	X = data.drop('price', axis=1)
	X = X.drop(X.columns[0], axis=1)
	y = data['price'].apply(price_func)

	colt = compose.ColumnTransformer([
		('cat', OneHotEncoder(), ['category']),
		#('const', 'passthrough', ['const']),
		('title', WordEncoder(limit=title_lim), ['title']),
		('description', WordEncoder(limit=desc_lim), ['description'])])
	pipe = Pipeline([
        ('transform', colt),
        ('est', LinearRegression())
    ])
	pipe.fit(X,y)
	y_pred = pipe.predict(X)
	print(len(data.index))
	print(metrics.r2_score(y,y_pred))
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
	title = '18" tall metal bed frame'
	desc = 'Selling an 18" tall metal bed frame. Comes apart at corners for easy assembly. Great for condo as the height is perfect for under bed storage bins or luggate. Frame is in near perfect condition.  Comes with wooden slats.'
	sample_X = pd.DataFrame({'url':[''], 'title':[title], 'distance':[''], 'description':[desc], 'location':[''], 'time_offset':[datetime.now()], 'retreived':[datetime.now()], 'category':['bed-mattress']})
	print(sample_X)
	sample_y = pipe.predict(sample_X)[0]
	print(math.exp(sample_y)-25)
