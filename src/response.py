import errors

from collections import defaultdict
from datetime import datetime


class TopViewsResponse:
    def __init__(self, json, start_date, end_date):
        self.article_views = self.parse_json(json)
        """A list of hashes describing cumulative article views for the most viewed
        articles between start_date and end_date"""
        self.start_date = start_date.strftime("%Y/%m/%d")
        """The start date of the json data from which views are counted"""
        self.end_date = end_date.strftime("%Y/%m/%d")
        """The end date of the json data until which views are counted (inclusive)"""

    def parse_json(self, response):
        """
        Expects:
        A list of daily json responses from the WikiMedia PageViews most viewed
        articles endpoint where each response has the format
        {
                "items":[{
                        "project":"en.wikipedia",
                        "access":"all-access",
                        "year":"2023",
                        "month":"07",
                        "day":"29",
                        "articles": [{"article":"Main_Page","views":4430453,"rank":1}, ...}]
                }]
        }

        Returns:
        A list of hashes describing cumulative article views for all the days
        provided in the json input with the format
        [
                {
                        'rank': <ranking based on total views>,
                        'article': <article name>,
                        'views': <total cumulative views>
                }, ...
        ]
        """
        article_views = defaultdict(int)
        try:
            for daily_result in response:
                for item in daily_result["items"]:
                    articles = item["articles"]
                    for article in articles:
                        name = article["article"]
                        views = article["views"]
                        article_views[name] += views
        except Exception as e:
            raise errors.ParseResponseException(str(e))

        result = []
        for idx, key in enumerate(
            sorted(article_views, key=article_views.get, reverse=True)
        ):
            result.append(
                {"rank": idx + 1, "article": key, "views": article_views[key]}
            )

        return result


class DateWithMostViewsResponse:
    def __init__(self, json, article):
        result = self.parse_json(json)
        self.date = result["dates"]
        """The date(s) on which the article had the most views"""
        self.views = result["views"]
        """The number of page views on the above date(s)"""
        self.article = article
        """The name of the article"""

    def parse_json(self, response):
        top_ts = []
        top_views = 0
        try:
            for daily_result in response:
                for item in daily_result["items"]:
                    views = item["views"]
                    ts = item["timestamp"][:-2]  # Drop the hours on the date
                    if views > top_views:
                        top_views = views
                        top_ts = [ts]
                    elif views == top_views:
                        top_ts.append(ts)
        except Exception as e:
            raise errors.ParseResponseException(str(e))

        dates = [
            (datetime.strptime(ts, "%Y%m%d").strftime("%Y/%m/%d")) for ts in top_ts
        ]
        return {"views": top_views, "dates": dates}


class ArticleViewsResponse:
    def __init__(self, json, article, start_date, end_date):
        self.views = self.sum_views(json)
        """The number of views for the article from start_date to end_date"""
        self.article = article
        """The name of the article"""
        self.start_date = start_date.strftime("%Y/%m/%d")
        """The start date of the json data from which views are counted"""
        self.end_date = end_date.strftime("%Y/%m/%d")
        """The end date of the json data until which views are counted (inclusive)"""

    def sum_views(self, response):
        try:
            return sum([item["views"] for item in response["items"]])
        except Exception as e:
            raise errors.ParseResponseException(str(e))
