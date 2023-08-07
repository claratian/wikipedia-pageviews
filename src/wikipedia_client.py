# Wikipedia client
#!/usr/bin/env python 

import datetime
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dateutil.parser import parse


'''
Requirements: datetime, dateutil, calendar, attrdict
'''

'''
- Retrieve a list of the most viewed articles for a week or a month (You can get the most
viewed articles for a day and their view count. To calculate the most articles for a week
or month, you can assume that an article that is listed for one day but not listed for
another day has 0 views when it’s not listed)
● For any given article, be able to get the view count of that specific article for a week or a
month
● Retrieve the day of the month where an article got the most page views

'''

CLIENT_URL = "https://github.com/claratian"
USER_AGENT = "Python Wikipedia PageView client <{url}>"
HEADERS = {
	'User-Agent': USER_AGENT.format(url=CLIENT_URL)
}

BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
PROJECT = "en.wikipedia"

TOP_ARTICLES = "top"
TOP_PARAMS = "{project}/all-access/{date}"

PER_ARTICLE = "per-article"
PER_ARTICLE_PARAMS = "{project}/all-access/all-agents/{article}/{granularity}/{start}/{end}"


class ZeroOrNotLoadedDataException(Exception):
	"""
	Raised for 404 Error

	Either there are 0 pageviews for the given project, timespan and filters 
	specified in the query, or the requested data (like a request for the current day)
	has not yet been loaded into the API's database yet.
	https://wikitech.wikimedia.org/wiki/Analytics/PageviewAPI#Gotchas
	"""
	def __init__(self, date):
		self.message = "0 pageviews for {date} or data not available".format(date=date)
		self.date = date

class ThrottlingException(Exception):
	"""
	Raised for 429 Error

  Client has made too many requests and it is being throttled. 
  This will happen if the storage cannot keep up with the request ratio from a given IP
	https://wikitech.wikimedia.org/wiki/Analytics/PageviewAPI#Gotchas
	"""
	def __init__(self):
		self.message = "Too many requests made"

#Write a test for the method below
def top_articles(dates):
	params_list = [TOP_PARAMS.format(project=PROJECT, date=date) for date in dates]
	urls = [__url(TOP_ARTICLES, params) for params in params_list]

	return __get_pageviews_concurrent(urls, dates)

def unit_test_top_articles():
	dates = ['20180101', '20180102', '20180103']
	top_articles(dates)

def views_per_article_by_day(article, dates, granularity):
	params_list = [PER_ARTICLE_PARAMS.format(project=PROJECT,
                          article=article,
                          start=date,
                          end=date,
                          granularity=granularity) for date in dates]
	urls = [__url(PER_ARTICLE, params) for params in params_list]
	return __get_pageviews_concurrent(urls, dates)
	
   
def views_per_article(article, start_date, end_date, granularity):
    article = "_".join(article.split(" "))

    params = PER_ARTICLE_PARAMS.format(project=PROJECT,
                          article=article,
                          start=start_date,
                          end=end_date,
                          granularity=granularity)
    url = __url(PER_ARTICLE, params)
    return __get_pageviews(url, (start_date, end_date))

def __get_pageviews_concurrent(urls, dates):
	results = []
	errors = []
	url_dates = zip(urls, dates)
	with ThreadPoolExecutor() as executor:
		future_results = [executor.submit(__get_pageviews, url, date) for url, date in url_dates]
		for future in as_completed(future_results):
			try:
				results.append(future.result())
			except Exception as e:
				errors.append(e.message)
	if len(errors):
		raise Exception(str(errors))
	return results

def __get_pageviews(url, date):
	"""Calls Wikimedia API at the given url"""
	
	response = requests.get(url, headers=HEADERS)

	if response.status_code == 200:
		return response.json()	
	elif response.status_code == 404:
		raise ZeroOrNotLoadedDataException(date)
	elif response.status_code == 429:
		raise ThrottlingException
	else:
		response.raise_for_status()

def __url(endpoint, params):
		return "/".join([BASE_URL, endpoint, params])



