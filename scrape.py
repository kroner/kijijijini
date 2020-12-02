import requests
import dill
import os
import re
import sys
import numpy as np
import pandas as pd
import time
import categories
import datetime
from bs4 import BeautifulSoup
#from concurrent.futures import as_completed
#from requests_futures.sessions import FuturesSession

url = 'https://www.kijiji.ca/b-{0}/{1}/page-{2}/c{3}l{4}'
SLEEP_TIME = 60 # seconds to wait if no results are returned
FAIL_CAP   =  1 # max number of failures before ending
TRIES      =  5 # number of times to try the same query before failing
SAVE_PATH  = '/home/robert/Dropbox/TDI/kijijijini/data/'
LOCATION   = 'city-of-toronto'

location_codes = {
	'city-of-toronto':'1700273'
	}


def extract_text(div):
	if div == None:
		return ''
	return div.text.strip()


def page_df(response):
	soup = BeautifulSoup(response.text, "lxml")
	listings_divs = soup.find_all('div', class_='regular-ad')
	listings_divs = [div for div in listings_divs if len(div['class']) <= 2]
	info = {'url':[], 'price':[], 'title':[], 'description':[], 'location':[], 'post_date':[], 'retreived':[]}
	index = []
	for div in listings_divs:
		loc_time = extract_text(div.find('div', class_='location'))
		if loc_time == '': loc_time = ['']
		else: loc_time = loc_time.split('\n')
		price = extract_text(div.find('div', class_='price'))
		if price == 'Free':
			price = 0.0
		else:
			try:
				price = float(re.sub(r'[^\d\-.]', '', price))
			except (TypeError, ValueError):
				continue
		index.append(int(div['data-listing-id']))
		#info['id'].append(int(div['data-listing-id']))
		info['url'].append(div['data-vip-url'])
		info['price'].append(price)
		info['title'].append(extract_text(div.find('div', class_='title')))
		#info['distance'].append(extract_text(div.find('div', class_='distance')))
		info['description'].append(extract_text(div.find('div', class_='description')))
		info['location'].append(loc_time[0])
		info['post_date'].append(post_date(datetime.datetime.now(), loc_time[-1]))
		info['retreived'].append(datetime.datetime.now())

	df = pd.DataFrame(info, index=index)
	df.index.name = 'id'
	if len(df.index) == 0:
		df = None
	return df


def try_page(page_url, get_count=False):
	for _ in range(TRIES):
		response_code = 0
		try: response = requests.get(page_url)
		except (TypeError, AttributeError, ConnectionError):
			print('!', end='', flush=True, file=sys.stdout)
			continue
		response_code = response.status_code
		if response_code != 200:
			continue
		if get_count:
			soup = BeautifulSoup(response.text, "lxml")
			div = soup.find('div',  class_='showing')
			if div is None:
				continue
			return int(div.text.split()[-2].replace(',',''))
		df = page_df(response)
		if df is None:
			print('z', end='', flush=True, file=sys.stdout)
			time.sleep(SLEEP_TIME)
			continue
		else:
			return df
	print('\npage {0} response code {1}.'.format(page,response_code), flush=True, file=sys.stderr)
	return None


def scrape(item, start_date=None, location=LOCATION, start_page=1, end_page=101, file_path=None):
	if file_path is not None:
		out_file = open(file_path, 'w')
	page_url = url.format(item, location, 1, categories.item_code(item), location_codes[location])
	listings = try_page(page_url, get_count=True)
	end_page = min([(listings-1)//40 + 2, end_page])

	print(item, listings, flush=True, file=sys.stdout)

	page_dfs = []
	fail_count = 0
	for page in range(start_page, end_page):
		if page % 10 == 9: print('.', end='', flush=True)
		fail = True
		page_url = url.format(item, location, page, categories.item_code(item), location_codes[location])
		df = try_page(page_url)
		if df is None:
			fail_count += 1
			if fail_count >= FAIL_CAP:
				print('stopped at page {0}.'.format(page), flush=True, file=sys.stderr)
				break
		else:
			if file_path is not None:
				df.to_csv(out_file, header=(page == 0))
			#df.to_sql(name='listings', con=db.engine)
			#db.session.commit()
			page_dfs.append(df)
			if start_date is not None and df['post_date'].iloc[-1] < start_date:
				break
	if file_path is not None:
		out_file.close()
	print('', file=sys.stdout)
	if len(page_dfs) > 0:
		df = pd.concat(page_dfs)
		df['item_id'] = categories.item_dict[item]
		return df
	return None


def collect_all(location=LOCATION, item=None, start_item=0, save_path=SAVE_PATH):
	if item == None: items = [item[0] for item in categories.item_list][start_item:]
	else: items = [item]
	for item in items:
		file_path = save_path + 'kdat-{0}.csv'.format(item)
		df = scrape(item, location=location, file_path=file_path)

def csv_to_df(item, save_path=SAVE_PATH):
	file_path = 'data/kdat-' + item + '.csv'
	data_file = open(file_path, 'r')
	df = pd.read_csv(data_file, index_col=0)
	data_file.close()

	df.rename(columns={'Unnamed: 0':'id'}, inplace=True)
	df['item_id'] = categories.item_dict[item]
	df['price'] = df['price'].apply(int)
	df['retreived'] = df['retreived'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'))
	df['post_date'] = df.apply(lambda row: post_date(row['retreived'], row['time_offset']), axis=1)
	return df[['url','price','title','description','location','post_date','retreived','item_id']]


# find the post date for listing retreived at t and with time string st
def post_date(t, st):
	offset = datetime.timedelta()
	try:
		t = datetime.datetime.strptime(st, '%d/%m/%Y')
	except(ValueError):
		if re.match(r'Yesterday', st) is not None:
			offset = datetime.timedelta(days=1)
		m = re.match(r'< ([0-9]+) h', st)
		if m is not None:
			offset = datetime.timedelta(hours=int(m.group(1)))
	return (t - offset).date()

if __name__ == '__main__':
	#collect_all(start_item=141)
	pass
