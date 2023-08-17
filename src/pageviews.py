import wikipedia_client
import response

from calendar import monthrange
from datetime import datetime, timedelta, date
from dateutil.parser import parse
from errors import InvalidInputException


WEEKLY_VIEWS_OUTPUT = "Page views for {article} between {start} and {end}: {views}\n"
MONTHLY_VIEWS_OUTPUT = "Page views for {article} during {month} {year}: {views}\n"

TOP_WEEKLY_VIEWS_OUTPUT = "Top page views for week of {start}-{end}:\n{views}\n"
TOP_MONTHLY_VIEWS_OUTPUT = "Top page views for {month} {year}:\n{views}\n"

DAY_OF_MONTH_MOST_VIEWS_OUTPUT = "The day(s) of {month} where {article} was most viewed was \
 {date}, with {views} views\n"

# Granularity levels for views per article
DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"

DAYS_IN_WEEK = 7


def views_per_article(granularity, article, date):
    """
    Expects:
    The name of a Wikipedia article, a valid non-abbreviated month name, and optionally a year
    (both int and string supported). If no year is provided the current year will be used.

    Returns:
    An ArticleViewsResponse object with attributes
    - views: the number of views the article received in the month
    - article: the name of the requested article
    - start date: start date of the returned article data (the start of the requested month)
    - end date: end date of the returned article data (the end of the requested month)
    """
    if granularity == MONTHLY:
        start_date, end_date, _ = __date_range_for_month(date)
        search_granularity = MONTHLY
    elif granularity == WEEKLY:
        start_date, end_date = __date_range_for_week(date)
        search_granularity = DAILY
    else:
        raise InvalidInputException(
            "Top viewed articles granularity must be 'weekly' or 'monthly', got {g} instead".format(
                g=granularity
            )
        )
    start_formatted, end_formatted = __format_date(start_date), __format_date(end_date)
    response_json = wikipedia_client.views_per_article(
        article, start_formatted, end_formatted, search_granularity
    )
    result = response.ArticleViewsResponse(
        response_json, article, start_date.date(), end_date.date()
    )

    return result


def top_views(granularity, date):
    if granularity == MONTHLY:
        start_date, _, month_length = __date_range_for_month(str(date))
        dates = [start_date + timedelta(days=x) for x in range(month_length)]
    elif granularity == WEEKLY:
        start_date = __parse_full_date(str(date))
        dates = [start_date + timedelta(days=x) for x in range(DAYS_IN_WEEK)]
    else:
        raise InvalidInputException(
            "Top viewed articles granularity must be 'weekly' or 'monthly', got {g} instead".format(
                g=granularity
            )
        )
    query_dates = [__format_date(date, use_separators=True) for date in dates]
    response_json = wikipedia_client.top_articles(query_dates)
    result = response.TopViewsResponse(response_json, start_date, dates[-1])

    return result


def day_of_month_with_most_views(article, year_month):
    start_date, _, month_length = __date_range_for_month(str(year_month))
    dates = [start_date + timedelta(days=x) for x in range(month_length)]
    query_dates = [__format_date(date) for date in dates]

    response_json = wikipedia_client.views_per_article_by_day(
        article, query_dates, DAILY
    )
    result = response.DateWithMostViewsResponse(response_json, article)
    return result


def __week_from_date(date):
    return date + timedelta(days=DAYS_IN_WEEK - 1)


def __date_range_for_week(year_month_day):
    start_date = __parse_full_date(year_month_day)
    end_date = start_date + timedelta(days=DAYS_IN_WEEK - 1)
    return start_date, end_date


def __date_range_for_month(year_month):
    try:
        year_month_arr = year_month.split("-")
        if len(year_month_arr) == 2:
            year, month = int(year_month_arr[0]), int(year_month_arr[1])
        month_length = monthrange(year, month)[1]
        start_date = datetime(year, month, 1)
        end_date = start_date + timedelta(days=month_length - 1)
        return start_date, end_date, month_length
    except Exception as e:
        raise InvalidInputException(
            "Year and month must be in valid ISO 8601 format (yyyy-mm)."
        )


def __parse_full_date(year_month_day):
    try:
        return datetime.strptime(year_month_day, "%Y-%m-%d")
    except Exception as e:
        raise InvalidInputException(
            "Year, month, and day must be in valid ISO 8601 format (yyyy-mm-dd)."
        )


def __format_date(date: datetime, use_separators=False):
    if use_separators:
        return date.strftime("%Y/%m/%d")
    else:
        return date.strftime("%Y%m%d")
