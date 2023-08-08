import wikipedia_client
import response

from calendar import monthrange
from datetime import datetime, timedelta, date
from dateutil.parser import parse
from errors import InvalidInputError

'''
for readme:
	date can be formatted as yyyy/mm/dd, yyyy/m/d, yyyy-mm-dd, or yyyy-m-d
	when providing a monthly or weekly range, if part of the range is invalid (in the future), only results of days for which the api has data will be returned
	month must be the full string name of the month (lowercase or capitalization doesn't matter) - 
	can handle mispelled month but formatting of output into proper capitalization is disregarded.
	year is optional but if not provided will default to current year

'''
CURR_YEAR = date.today().year

WEEKLY_VIEWS_OUTPUT = "Page views for {article} between {start} and {end}: {views}"
MONTHLY_VIEWS_OUTPUT = "Page views for {article} during {month} {year}: {views}"

TOP_WEEKLY_VIEWS_OUTPUT = "Top page views for week of {start}-{end}:\n{views}"
TOP_MONTHLY_VIEWS_OUTPUT = "Top page views for {month} {year}:\n{views}"

DAY_OF_MONTH_MOST_VIEWS_OUTPUT = "The day(s) of {month} where {article} was most viewed was {date}, with {views} views"

# Granularity levels for views per article
DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"

DAYS_IN_WEEK = 7

def weekly_views_per_article(article, from_date):
	'''
	Expects:
	The name of a Wikipedia article and a valid date in the format yyyy/mm/dd, yyyy/m/d, yyyy-mm-dd, 
	or yyyy-m-d that indicates the date from which the week being queried for starts.

	Returns:
	An ArticleViewsResponse object with attributes
	- views: the number of views the article received in the week
	- article: the name of the requested article
	- start date: start date of the returned article data (the provided from_date)
	- end date: end date of the returned article data (the date of the last day of the 
	requested week) 
	'''
	try:
		article = str(article)
		__validate_article(article)
		start_date, end_date = __date_range_for_week(str(from_date))
		start_formatted, end_formatted = __format_date(start_date), __format_date(end_date)

		response_json = wikipedia_client.views_per_article(
			article, 
			start_formatted, 
			end_formatted, 
			DAILY
		)
		result = response.ArticleViewsResponse(response_json, article, start_date.date(), end_date.date())
		print(WEEKLY_VIEWS_OUTPUT.format(
			article=result.article, 
			start=result.start_date, 
			end=result.end_date, 
			views=result.views
		))
		return result
	except Exception as e:
		print("Failed to get weekly views per article: {err}".format(err=str(e)))

def monthly_views_per_article(article, month_name, year=CURR_YEAR):
	'''
	Expects:
	The name of a Wikipedia article, a valid non-abbreviated month name, and optionally a year 
	(both int and string supported). If no year is provided the current year will be used.

	Returns:
	An ArticleViewsResponse object with attributes
	- views: the number of views the article received in the month
	- article: the name of the requested article
	- start date: start date of the returned article data (the start of the requested month)
	- end date: end date of the returned article data (the end of the requested month) 
	'''
	try:
		article = str(article)
		__validate_article(article)
		start_date, end_date, _ = __date_range_for_month(month_name, int(year))
		start_formatted, end_formatted = __format_date(start_date), __format_date(end_date)

		response_json = wikipedia_client.views_per_article(
			article, 
			start_formatted, 
			end_formatted, 
			MONTHLY
		)
		result = response.ArticleViewsResponse(response_json, article, start_date.date(), end_date.date())
		print(MONTHLY_VIEWS_OUTPUT.format(article=article, month = month_name, year=year, views=result.views))
		return result
	except Exception as e:
		print("Failed to get monthly views per article: {err}".format(err=str(e)))

def top_weekly_views(from_date):
	'''
	Expects:
		A valid date in the format yyyy/mm/dd, yyyy/m/d, yyyy-mm-dd, or yyyy-m-d that indicates
		the date from which the week being queried for starts.

	Returns:
		A TopViewsResponse object with an article_views attribute that contains a list of hashes 
		describing cumulative top article views for the week starting from the provided start
		date ordered from most to least views with the format
		[
			{'rank': <ranking based on total views>, 'article': <article name>, 'views': <total cumulative views>},
			...
		]
	'''
	try:
		start_date = __parse_date(str(from_date))
		dates = [start_date + timedelta(days=x) for x in range(DAYS_IN_WEEK)]
		query_dates = [__format_date(date, use_separators=True) for date in dates]
		response_json = wikipedia_client.top_articles(query_dates)
		result = response.TopViewsResponse(response_json, start_date, dates[-1])
		print(TOP_WEEKLY_VIEWS_OUTPUT.format(start=result.start_date, end=result.end_date, views=result.article_views))
		return result
	except Exception as e:
		print("Failed to get top weekly views: {err}".format(err=str(e)))

def top_monthly_views(month_name, year=CURR_YEAR):
	'''
	Expects:
		A valid, non-abbreviated month name and optionally a year.
		If no year is provided the current year will be used.

	Returns:
		A TopViewsResponse object with an article_views attribute that contains a list of hashes 
		describing cumulative top article views for the month and year provided ordered from most to 
		least views with the format
		[
			{'rank': <ranking based on total views>, 'article': <article name>, 'views': <total cumulative views>},
			...
		]
	'''
	try:
		start_date, _, month_length = __date_range_for_month(month_name, int(year))
		dates = [start_date + timedelta(days=x) for x in range(month_length)]
		query_dates = [__format_date(date, use_separators=True) for date in dates]
		response_json = wikipedia_client.top_articles(query_dates)
		result = response.TopViewsResponse(response_json, start_date, dates[-1])

		print(TOP_MONTHLY_VIEWS_OUTPUT.format(month=month_name, year=year, views=result.article_views))
		return result
	except Exception as e:
		print('Failed to get top monthly views: {err}'.format(err=str(e)))

def day_of_month_with_most_views(article, month_name, year=CURR_YEAR):
	'''
	Expects:
		An article name, a valid non-abbreviated month name, and optionally a year. 
		If no year is provided the current year will be used.
	Returns:
		A DateWithMostViewsResponse object with attributes 
		- date: a list of timestamps representing the date (or dates if multiple days are tied)
			   the article received the most views in the month
		- views: the number of views for the article on the returned date(s)
		- article: the name of the requested article
	'''
	try:
		article = str(article)
		__validate_article(article)
		start_date, _, month_length = __date_range_for_month(month_name, int(year))
		dates = [start_date + timedelta(days=x) for x in range(month_length)]
		query_dates = [__format_date(date) for date in dates]

		response_json = wikipedia_client.views_per_article_by_day(
			article, 
			query_dates,
			DAILY
		)
		result = response.DateWithMostViewsResponse(response_json, article)
		print(DAY_OF_MONTH_MOST_VIEWS_OUTPUT.format(article=article, month=month_name, year=str(year), date=result.date, views=result.views))
		return result
	except Exception as e:
		print("Failed to get day of month with most views: {err}".format(err=str(e)))

def __date_range_for_week(start_date):
	start_date = __parse_date(start_date)
	end_date = start_date + timedelta(days = DAYS_IN_WEEK-1)
	return start_date, end_date

def __date_range_for_month(month_name, year):
	try:
		month = datetime.strptime(month_name, '%B').month
	except Exception as e:
		raise InvalidInputError("Month entered must be valid full month name (e.g. July, August)")
	month_length = monthrange(year, month)[1]
	start_date = datetime(year, month, 1)
	end_date = start_date + timedelta(days=month_length-1)
	return start_date, end_date, month_length

def __parse_date(string_date):
	for fmt in ('%Y/%m/%d', '%Y-%m-%d'):
		try:
			return datetime.strptime(string_date, fmt)
		except ValueError:
			pass
	raise InvalidInputError(
		"Provided date must be in the format yyyy/mm/dd, yyyy/m/d, yyyy-mm-dd, or yyyy-m-d"
	)

def __format_date(date, use_separators=False):
	if use_separators:
		return date.strftime('%Y/%m/%d')
	else:
		return date.strftime('%Y%m%d')

def __validate_article(article_name):
	if not article_name:
		raise InvalidInputError("Article name must not be blank")

day_of_month_with_most_views("Barbie (film)", "July")
#monthly_views_per_article("Barbie (film)", "July")
#weekly_views_per_article("Barbie (film)", "2000/08/01")
#top_weekly_views("2020/08/01")
#top_monthly_views("July")




