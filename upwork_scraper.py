import requests
import re
from datetime import datetime
from time import sleep
import random
import os
import logging
import sys

from bs4 import BeautifulSoup as soup

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('./upwork_scraper.log'), logging.StreamHandler()])

class Scraper:

    def __init__(self, cat):

        cats = {
            'All Categories': 'all',
            'Data Science & Analytics':'data-science-analytics',
            'Web, Mobile & Software Dev':'web-mobile-software-dev',
            'IT & Networking':'it-networking',
            'Engineering & Architecture ':'engineering-architecture',
            'Design & Creative':'design-creative',
            'Writing':'writing',
            'Translation':'translation',
            'Legal':'legal',
            'Admin Support':'admin-support',
            'Customer Service':'customer-service',
            'Sales & Marketing':'sales-marketing',
            'Accounting & Consulting':'accounting-consulting'
        }
        self.cat = cats[cat]
        self.USER_AGENT_LIST = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
            'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        ]
        self.output = None
        self.current_date = datetime.now().date().strftime("%Y-%m-%d")

        for dir_name in ['./data', './data/%s' % self.cat, './data/%s/%s' % (self.cat, self.current_date)]:
            try:
                os.stat(dir_name)
            except:
                os.mkdir(dir_name)

        if os.path.isfile('./last_dt.txt'):
            self.last_dt = datetime.strptime(open('./last_dt.txt', 'r').readline(), '%Y-%m-%d %H:%M:%S')
        else:
            self.last_dt = datetime(1970, 1, 1)

    def makeUrl(self, page):
        if self.cat == 'all':
            return "https://www.upwork.com/o/jobs/browse/?page=%i" % page + '&sort=create_time%2Bdesc'
        return "https://www.upwork.com/o/jobs/browse/c/%s/?page=%i" % (self.cat, page) + '&sort=create_time%2Bdesc'

    def wait(self, agent, page):
        flag = True
        while True:
            try:
                response = requests.request('GET', self.makeUrl(page), timeout=60, headers={'User-Agent': agent})
                logging.info('Got the page!')
                return response
            except requests.ConnectionError:
                if flag:
                    logging.error('Connection lost! Waiting for connection...')
                    flag = False
                sleep(2)
                pass

    def scrap(self):
        i = 1
        agent = self.USER_AGENT_LIST[-1]
        while True:
            logging.info('Requsting new page...')
            
            #10% chance to change agent
            if random.choice(range(100)) <= 10:
                agent = random.choice(self.USER_AGENT_LIST)

            response = self.wait(agent, i)
            if response.status_code != 200:
                if response.status_code == 403:
                    logging.error('Security check not passed :(')
                elif response.status_code == 404:
                    logging.error('Page not found!')
                break
            response = response.text

            logging.info('Grab page #%i...' % i)
            page_soup = soup(response, 'html.parser')
            output = page_soup.find_all('a', class_='job-title-link break visited')
            if self.output == output:
                logging.info('All pages grabbed! Finished!')
                break
            self.output = output

            dt = str(page_soup.body.find_all('span', class_='js-posted')[0].time)
            dt = ' '.join(re.split('"|\+|T', dt)[1:3])
            dt = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            if i == 1:
                with open('./last_dt.txt', 'w') as f:
                    f.write(dt.strftime("%Y-%m-%d %H:%M:%S"))
            
            if dt > self.last_dt:
                with open('./data/%s/%s' % (self.cat, self.current_date+'/page_%s.html' % i), 'w') as f:
                    f.write(response)
                    logging.info('File #%i saved!' % i)
                sleep(random.randint(3,8))
                i += 1
            else:
                logging.info('There is no new jobs!')
                break

if __name__ == '__main__':
    Scraper(sys.argv[1]).scrap()