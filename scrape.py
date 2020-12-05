import requests
import dill
import os
import re
import sys
import numpy as np
import pandas as pd
import time
import datetime
from bs4 import BeautifulSoup
#from concurrent.futures import as_completed
#from requests_futures.sessions import FuturesSession

url = 'https://www.kijiji.ca/b-{0}/{1}/page-{2}/c{3}l{4}'
url2 = 'https://www.kijiji.ca/v-/a/a/{0}'
SLEEP_TIME =  60 # seconds to wait if no results are returned
FAIL_CAP   =   5 # max number of failures before ending
TRIES      =   5 # number of times to try the same query before failing
PAGE_LIMIT = 100 # search depth (100 is the limit imposed by Kijiji)
CHAR_LIMIT = 200 # max description length (200 is the limit imposed by Kijiji)
SAVE_PATH  = '/home/robert/Dropbox/TDI/kijijijini/data/'
LOCATION   = 'city-of-toronto'

location_codes = {
	'city-of-toronto':'1700273'
	}


def extract_text(div):
	if div == None:
		return ''
	return div.text.strip()

def extract_price(div):
	price = extract_text(div)
	if price == 'Free':
		price = 0.0
	else:
		price = float(re.sub(r'[^\d\-.]', '', price))
	return price

# Take a response for a search page request and parse out the data for the
# listing that appear.
def parse_search_page(response):
	soup = BeautifulSoup(response.text, 'html.parser')
	listings = None
	listings_divs = soup.find_all('div', class_='regular-ad')
	if len(listings_divs) == 0:
		raise LookupError('response is missing the expected elements.')
	listings_divs = [div for div in listings_divs if len(div['class']) <= 2]
	info = {'url':[], 'price':[], 'title':[], 'description':[], 'location':[], 'post_date':[], 'retreived':[]}
	index = []
	for div in listings_divs:
		loc_time = extract_text(div.find('div', class_='location'))
		if loc_time == '':
			loc_time = ['']
		else:
			loc_time = loc_time.split('\n')
		#info['id'].append(int(div['data-listing-id']))
		try:
			info['price'].append(extract_price(div.find('div', class_='price')))
			info['url'].append(div['data-vip-url'])
			info['title'].append(extract_text(div.find('div', class_='title')))
			#info['distance'].append(extract_text(div.find('div', class_='distance')))
			info['description'].append(extract_text(div.find('div', class_='description')))
			info['location'].append(loc_time[0])
			info['post_date'].append(post_date(datetime.datetime.now(), loc_time[-1]))
			info['retreived'].append(datetime.datetime.now())
			index.append(int(div['data-listing-id']))
		except (TypeError, ValueError):
			continue

		div = soup.find('div', class_='showing')
		if div is not None:
			listings = int(div.text.split()[-2].replace(',',''))
	df = pd.DataFrame(info, index=index)
	df.index.name = 'id'
	if len(df.index) == 0:
		df = None
	return (df, listings)

# Take a response for a search page request and parse out the data for the
# listing that appear.
def parse_listing_page(response):
	info = dict()
	soup = BeautifulSoup(response.text, 'html.parser')
	title_obj = soup.find('h1', itemprop='name')
	if title_obj is None:
		raise LookupError('response is missing the expected elements.')
	info['title'] = extract_text(title_obj)
	dobj = soup.find('div', itemprop='description')
	desc = ' '.join([extract_text(p) for p in dobj('p')])
	info['description'] = standardize_desc(desc, CHAR_LIMIT)
	urls = soup.find_all('a', itemprop='url')
	info['url'] = urls[-1].get('href')
	info['item_id'] = url_item(info['url'])
	info['price'] = extract_price(soup.find('span', itemprop='price'))

	return info

def url_item(url):
	matches = re.findall(r'c([0-9]+)l[0-9]+', url)
	return int(matches[-1])

def search_url(st):
	id = st.split(sep='/')[-1]
	return url2.format(id)

def standardize_desc(desc, n):
	desc = ' '.join(desc.split())
	if len(desc) > n:
		i = desc[:n+1].rindex(' ')
		desc = desc[:i] + '\n...'
	return desc

# Tries to get a response for a search page (if page_num is given) or a listing
# page (if page_num is None).  Tries TRIES times before giving up.
def try_page(page_url, page_num=None):
	for _ in range(TRIES):
		response_code = 0
		try:
			response = requests.get(page_url)
		#except (TypeError, AttributeError, ConnectionError):
		except:
			print('!', end='', flush=True, file=sys.stdout)
			continue
		response_code = response.status_code
		if response_code != 200:
			continue
		try:
			if page_num is not None:
				out = parse_search_page(response)
			else:
				out = parse_listing_page(response)
			return out
		except LookupError:
			print('z', end='', flush=True, file=sys.stdout)
			time.sleep(SLEEP_TIME)
			continue
	if page_num is not None:
		raise LookupError(f'page {page_num} response code {response_code}.')
	else:
		raise LookupError(f'listing response code {response_code}.')


def scrape(item, start_date=None, location=LOCATION, start_page=1, end_page=PAGE_LIMIT+1):
	print(f'{item.name} ({item.id})', flush=True, file=sys.stdout)
	fail_count = 0
	page_dfs = []

	page = start_page
	while page < end_page:
		if page % 10 == 9: print('.', end='', flush=True)
		page_url = url.format(item.name, location, page, item.id, location_codes[location])
		try:
			(df, listings) = try_page(page_url, page_num=page)
		except LookupError:
			fail_count += 1
			if fail_count >= FAIL_CAP:
				print(f'Warning: stopped at page {page}.', flush=True, file=sys.stderr)
				break
		if page == start_page:
			if listings is not None:
				end_page = min([(listings-1)//40 + 2, end_page])
				print(f' current posted: {listings}\n ', end='', flush=True, file=sys.stdout)
		if df is not None:
			page_dfs.append(df)
			if start_date is not None and df['post_date'].iloc[-1] < start_date:
				break
		page += 1
	print('', file=sys.stdout)
	if len(page_dfs) > 0:
		df = pd.concat(page_dfs)
		df['item_id'] = item.id
		return df
	return None

# csv is an old format for storing the data
def csv_to_df(item, save_path=SAVE_PATH):
	file_path = 'data/kdat-' + item.name + '.csv'
	data_file = open(file_path, 'r')
	df = pd.read_csv(data_file, index_col=0)
	data_file.close()

	df.rename(columns={'Unnamed: 0':'id'}, inplace=True)
	df['item_id'] = item.id
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
