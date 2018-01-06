import re
from datetime import datetime
import os
import sys
import logging
import traceback

from bs4 import BeautifulSoup as soup
import pandas as pd
import numpy as np
import tqdm

def title(job):
    try:
        return ' '.join([i for i in re.split('\W+', job.find('a', class_='job-title-link break visited').text.strip().lower())
                         if len(i) > 2 and not i.isdigit()])
    except:
        return np.nan

def type_(job):
    try:
        return ' '.join([i for i in re.split('\W+', job.find('strong', class_='js-type').text.lower())
                         if i != 'price'])
    except:
        return np.nan

def level(job):
    try:
        return ' '.join([i for i in re.split('\W+', job.find('span', class_='js-contractor-tier').text.lower().strip())
                         if i != 'level']).strip()
    except:
        return np.nan

def budget(job):
    try:
        return int(' '.join(re.split('\W+', job.find('span', {'itemprop':"baseSalary"}).text)).strip())
    except:
        return np.nan

def key(job):
    k = job['data-key'][1:]
    if k:
        return k
    else:
        return np.nan

def time(job):
    t = ' '.join(re.split('"|\+|T', str(job.find_all('span', class_='js-posted')[0].time))[1:3])
    if t:
        return t
    else:
        return np.nan

def desc(job):
    d = ' '.join([i for i in re.split('\W+', job.find('div', class_="description break m-sm-top-bottom")['data-ng-init'].split('"')[1].replace("\\n", "").strip().lower())
                  if len(i) > 2 and not i.isdigit()])
    if d:
        return d
    else:
        return np.nan

def skills(job):
    sk = ' '.join(['_'.join(re.split('\W+', i.text.strip().lower())) for i in job.find_all('a', class_='o-tag-skill')])
    if sk:
        return sk
    else:
        return np.nan

class TqdmLoggingHandler(logging.Handler):

    def __init__ (self, level = logging.NOTSET):
        super (self.__class__, self).__init__ (level)

    def emit (self, record):
        try:
            msg = self.format (record)
            tqdm.tqdm.write (msg)
            self.flush()
        except:
            self.handleError(record)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('./upwork_parser.log'), TqdmLoggingHandler()])

if __name__ == '__main__':

	path = sys.argv[1]
	names = [os.path.join(dp, f) for dp, dn, filenames in os.walk(path) for f in filenames]
	names.sort(key=lambda x: os.stat(x).st_mtime)

	if os.path.isfile('./upwork_df.csv'):
	    df = pd.read_csv('./upwork_df.csv', index_col=0)
	else:
	    df = pd.DataFrame(columns=['budget', 'desc', 'key', 'level', 'skills', 'time', 'title', 'type'])

	logging.info('Start parsing pages...')

	for name in tqdm.tqdm(names, desc='pages'):

		try:    
		    page = open(name, 'r').read()
		    page_soup = soup(page, 'html.parser')
		    jobs = page_soup.body.find_all('section', class_='job-tile')

		    data = []

		    for job in jobs:
		        row = {
		            'key': key(job), 'title': title(job), 'time': time(job), 'type': type_(job), 
		            'level': level(job), 'budget': budget(job), 'desc': desc(job), 'skills': skills(job)
		        }
		        try:
		            if row['key'] not in df['key'].tolist():
		                data.append(row)
		        except:
		            continue
		        
		    df = df.append(pd.DataFrame(data), ignore_index=True).reset_index(drop=True)
		    
		    df.to_csv('./upwork_df.csv')

		except Exception as e:
			logging.error(traceback.format_exc())
			pass

	logging.info('Parsing finished!')
	logging.info('Dataframe shape: %i rows, %i columns' % (df.shape[0], df.shape[1]))