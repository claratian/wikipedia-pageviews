#!/usr/bin/env python3

import datetime
import json
import requests
from errors import ZeroOrNotLoadedDataException, ThrottlingException
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dateutil.parser import parse

CLIENT_URL = "https://github.com/claratian/pageviews"
USER_AGENT = "Python Wikipedia PageView client <{url}>"
HEADERS = {"User-Agent": USER_AGENT.format(url=CLIENT_URL)}

BASE_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
PROJECT = "en.wikipedia"

TOP_ARTICLES = "top"
TOP_PARAMS = "{project}/all-access/{date}"

PER_ARTICLE = "per-article"
PER_ARTICLE_PARAMS = (
    "{project}/all-access/all-agents/{article}/{granularity}/{start}/{end}"
)


def top_articles(dates):
    params_list = [TOP_PARAMS.format(project=PROJECT, date=date) for date in dates]
    urls = [__url(TOP_ARTICLES, params) for params in params_list]
    return __get_pageviews_concurrent(urls, dates)


def views_per_article_by_day(article, dates, granularity):
    params_list = [
        PER_ARTICLE_PARAMS.format(
            project=PROJECT,
            article=article,
            start=date,
            end=date,
            granularity=granularity,
        )
        for date in dates
    ]
    urls = [__url(PER_ARTICLE, params) for params in params_list]
    return __get_pageviews_concurrent(urls, dates)


def views_per_article(article, start_date, end_date, granularity):
    params = PER_ARTICLE_PARAMS.format(
        project=PROJECT,
        article=article,
        start=start_date,
        end=end_date,
        granularity=granularity,
    )
    url = __url(PER_ARTICLE, params)
    start_date_formatted = datetime.strptime(start_date, "%Y%m%d").strftime("%Y/%m/%d")
    end_date_formatted = datetime.strptime(end_date, "%Y%m%d").strftime("%Y/%m/%d")
    return __get_pageviews(url, [start_date_formatted, end_date_formatted])


def __get_pageviews_concurrent(urls, dates):
    results = []
    missing_data_dates = []
    url_dates = zip(urls, dates)
    with ThreadPoolExecutor() as executor:
        future_results = [
            executor.submit(__get_pageviews, url, [date]) for url, date in url_dates
        ]
        for future in as_completed(future_results):
            try:
                results.append(future.result())
            except ThrottlingException as t:
                raise t
            except ZeroOrNotLoadedDataException as z:
                missing_data_dates += z.dates
    if len(missing_data_dates):
        raise ZeroOrNotLoadedDataException(missing_data_dates)
    return results


def __get_pageviews(url, dates):
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise ZeroOrNotLoadedDataException(dates)
    elif response.status_code == 429:
        raise ThrottlingException
    else:
        response.raise_for_status()


def __url(endpoint, params):
    return "/".join([BASE_URL, endpoint, params])
