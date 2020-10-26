import requests
import dill
import os
import re
import numpy as np
import pandas as pd
import time
import categories
from datetime import datetime
from bs4 import BeautifulSoup
from concurrent.futures import as_completed
#from requests_futures.sessions import FuturesSession

url = 'https://www.kijiji.ca/b-{0}/{1}/page-{2}/c{3}l{4}'
SLEEP_TIME = 60 # seconds to wait if no results are returned
FAIL_CAP   =  1 # max number of failures before ending
TRIES      =  5 # number of times to try the same query before failing
SAVE_PATH  = 'data/'

location_codes = {
	'city-of-toronto':'1700273'
	}


def extract_text(div):
	if div == None: div = ''
	else: div = div.text.strip()
	return div


def page_df(response):
	soup = BeautifulSoup(response.text, "lxml")
	listings_divs = soup.find_all('div', class_='regular-ad')
	listings_divs = [div for div in listings_divs if len(div['class']) <= 2]
	info = {'url' : [], 'price' : [], 'title' : [], 'distance' : [], 'description' : [], 'location' : [], 'time_offset' : [], 'retreived' : []}
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
		info['url'].append(div['data-vip-url'])
		info['price'].append(price)
		info['title'].append(extract_text(div.find('div', class_='title')))
		info['distance'].append(extract_text(div.find('div', class_='distance')))
		info['description'].append(extract_text(div.find('div', class_='description')))
		info['location'].append(loc_time[0])
		info['time_offset'].append(loc_time[-1])
		info['retreived'].append(datetime.now())
	df = pd.DataFrame(info, index=index)
	if len(df.index) == 0:
		df = None
	return df


def listing_count(item, location):
	page_url = url.format(item, location, 0, categories.item_code(item), location_codes[location])
	response = requests.get(page_url)
	soup = BeautifulSoup(response.text, "lxml")
	return int(soup.find('div',  class_='showing').text.split()[-2].replace(',',''))


def try_page(page_url):
	for _ in range(TRIES):
		response_code = 0
		try: response = requests.get(page_url)
		except (TypeError, AttributeError, ConnectionError):
			print('!', end='', flush=True)
			continue
		response_code = response.status_code
		if response_code != 200:
			continue
		df = page_df(response)
		if df is None:
			print('z', end='', flush=True)
			time.sleep(SLEEP_TIME)
			continue
		else:
			return df
	print('\npage {0} response code {1}.'.format(page,response_code), flush=True)
	return None


def scrape(item, location, start_page=0, end_page=101, file_path=None):
	if file_path is None:
		out_file = None
	else:
		out_file = open(file_path, 'w')
	listings = listing_count(item, location)
	end_page = min([(listings-1)//40 + 1, end_page])

	print(item, listings, flush=True)

	page_dfs = []
	fail_count = 0
	for page in range(start_page, end_page):
		if page % 10 == 9: print('.', end='', flush=True)
		fail = True
		page_url = url.format(item, location,page, categories.item_code(item), location_codes[location])
		df = try_page(page_url)
		if df is None:
			fail_count += 1
			if fail_count >= FAIL_CAP:
				print('stopped at page {0}.'.format(page), flush=True)
				break
		else:
			df.to_csv(out_file, header=(page == 0))
			page_dfs.append(df)
	out_file.close()
	print('')
	if len(page_dfs) > 0:
		return pd.concat(page_dfs)


def collect_all(location, item=None, start_item=0, save_path=SAVE_PATH):
	if item == None: items = [item[0] for item in categories.item_list][start_item:]
	else: items = [item]
	for item in items:
		file_path = save_path + 'kdat-{0}.csv'.format(item)
		df = scrape(item, location, file_path=file_path)

def read_in_item_data(item, save_path=SAVE_PATH):
	file_path = 'data/kdat-' + item + '.csv'
	data_file = open(file_path, 'r')
	df = pd.read_csv(data_file)
	data_file.close()
	return df

if __name__ == '__main__':
	location = 'city-of-toronto'
	collect_all(location, start_item=141)
