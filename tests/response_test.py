import unittest

from context import errors, response
from datetime import datetime, date
from errors import ParseResponseException
from response import TopViewsResponse, DateWithMostViewsResponse, ArticleViewsResponse


class TopViewsResponseTest(unittest.TestCase):
    def test_init_response(self):
        day1 = {
            "items": [
                {
                    "articles": [
                        {"article": "foo", "views": 1},
                        {"article": "bar", "views": 2},
                    ]
                }
            ]
        }
        day2 = {
            "items": [
                {
                    "articles": [
                        {"article": "foo", "views": 3},
                        {"article": "bar", "views": 4},
                    ]
                }
            ]
        }
        result = response.TopViewsResponse(
            [day1, day2], datetime(2023, 7, 1), datetime(2023, 7, 7)
        )
        article_views = [
            {"rank": 1, "article": "bar", "views": 6},
            {"rank": 2, "article": "foo", "views": 4},
        ]
        self.assertEqual(result.article_views, article_views)
        self.assertEqual(result.start_date, "2023-07-01")
        self.assertEqual(result.end_date, "2023-07-07")

    def test_exception(self):
        day1 = {
            "items": [
                {
                    "articles": [
                        {"article": "foo", "views": 1},
                        {"article": "bar", "views": 2},
                    ]
                }
            ]
        }
        day2 = {
            "foo": [
                {
                    "articles": [
                        {"article": "foo", "views": 3},
                        {"article": "bar", "views": 4},
                    ]
                }
            ]
        }
        self.assertRaises(
            ParseResponseException,
            lambda: TopViewsResponse(
                [day1, day2], datetime(2023, 7, 1), datetime(2023, 7, 7)
            ),
        )


class DateWithMostViewsResponseTest(unittest.TestCase):
    def test_init_response(self):
        day1 = {"items": [{"article": "foo", "timestamp": "2023070700", "views": 1}]}
        day2 = {"items": [{"article": "foo", "timestamp": "2023070800", "views": 2}]}
        result = DateWithMostViewsResponse([day1, day2], "foo")
        dates = ["2023-07-08"]

        self.assertEqual(result.date, dates)
        self.assertEqual(result.views, 2)
        self.assertEqual(result.article, "foo")

    def test_multiple_dates(self):
        day1 = {"items": [{"article": "foo", "timestamp": "2023070700", "views": 1}]}
        day2 = {"items": [{"article": "foo", "timestamp": "2023070800", "views": 2}]}
        day3 = {"items": [{"article": "foo", "timestamp": "2023070900", "views": 2}]}
        result = DateWithMostViewsResponse([day1, day2, day3], "foo")
        dates = ["2023-07-08", "2023-07-09"]

        self.assertEqual(result.date, dates)
        self.assertEqual(result.views, 2)
        self.assertEqual(result.article, "foo")

    def test_exception(self):
        day1 = {"items": [{"article": "foo", "timestamp": "2023070700", "views": 1}]}
        day2 = {"items": [{"article": "foo", "timestamp": "2023070800", "bar": 2}]}
        self.assertRaises(
            ParseResponseException,
            lambda: DateWithMostViewsResponse([day1, day2], "foo"),
        )


class ArticleViewsResponseTest(unittest.TestCase):
    def test_init_response(self):
        data = {
            "items": [{"article": "foo", "views": 10}, {"article": "foo", "views": 12}]
        }
        result = ArticleViewsResponse(data, "foo", date(2023, 7, 1), date(2023, 7, 7))
        self.assertEqual(result.views, 22)
        self.assertEqual(result.article, "foo")
        self.assertEqual(result.start_date, "2023-07-01")
        self.assertEqual(result.end_date, "2023-07-07")

    def test_exception(self):
        data = {"items": [{"article": "foo", "views": 10}, {"article": "foo", "v": 12}]}
        self.assertRaises(
            ParseResponseException,
            lambda: ArticleViewsResponse(
                data, "foo", date(2023, 7, 1), date(2023, 7, 7)
            ),
        )


if __name__ == "__main__":
    unittest.main()
