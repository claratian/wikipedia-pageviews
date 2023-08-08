from context import app, wikipedia_client, response

import unittest
import mock
from datetime import datetime, date
from mock import patch, PropertyMock


class WeeklyViewsPerArticleTest(unittest.TestCase):
    @patch("response.ArticleViewsResponse")
    @patch("wikipedia_client.views_per_article")
    def test_get_views_per_article(self, mock_views_per_article, mock_response):
        mock_data = {
            "items": [{"article": "foo", "views": 11}, {"article": "foo", "views": 12}]
        }
        mock_views_per_article.return_value = mock_data
        response_start_date = date(2023, 7, 1)
        response_end_date = date(2023, 7, 7)
        mock_response.return_value = response.ArticleViewsResponse(
            mock_data, "foo", response_start_date, response_end_date
        )

        result = app.weekly_views_per_article("foo", "2023-07-01")

        mock_views_per_article.assert_called_with(
            "foo", "20230701", "20230707", "daily"
        )
        mock_response.assert_called_with(
            mock_data, "foo", response_start_date, response_end_date
        )
        self.assertEqual(result, mock_response.return_value)
        self.assertEqual(result.views, 23)

    @patch("wikipedia_client.views_per_article")
    def test_exceptions_caught(self, mock_views_per_article):
        mock_views_per_article.side_effect = Exception("exception")
        try:
            app.weekly_views_per_article("foo", "2023/07/01")
        except Exception:
            self.fail("weekly_views_per_article raised Exception unexpectedly")


class MonthlyViewsPerArticleTest(unittest.TestCase):
    @patch("response.ArticleViewsResponse")
    @patch("wikipedia_client.views_per_article")
    def test_get_views_per_article(self, mock_views_per_article, mock_response):
        mock_data = {
            "items": [{"article": "foo", "views": 10}, {"article": "foo", "views": 12}]
        }
        mock_views_per_article.return_value = mock_data
        response_start_date = date(2023, 7, 1)
        response_end_date = date(2023, 7, 31)
        mock_response.return_value = response.ArticleViewsResponse(
            mock_data, "foo", response_start_date, response_end_date
        )

        result = app.monthly_views_per_article("foo", "July", "2023")

        mock_views_per_article.assert_called_with(
            "foo", "20230701", "20230731", "monthly"
        )
        mock_response.assert_called_with(
            mock_data, "foo", response_start_date, response_end_date
        )
        self.assertEqual(result, mock_response.return_value)
        self.assertEqual(result.views, 22)

    def test_exceptions_caught(self):
        try:
            # Invalid month input
            app.monthly_views_per_article("foo", "Jul", "2023")
            # No data available
            app.monthly_views_per_article("foo", "July", "2003")
        except Exception:
            self.fail("monthly_views_per_article raised Exception unexpectedly")


class TopWeeklyViewsTest(unittest.TestCase):
    @patch("response.TopViewsResponse")
    @patch("wikipedia_client.top_articles")
    def test_get_top_articles(self, mock_top_articles, mock_response):
        mock_data = [
            {
                "items": [
                    {
                        "articles": [
                            {"article": "foo", "views": 4},
                            {"article": "bar", "views": 2},
                        ]
                    }
                ]
            }
        ]
        mock_top_articles.return_value = mock_data
        response_start_date = datetime(2023, 7, 1)
        response_end_date = datetime(2023, 7, 7)
        mock_response.return_value = response.TopViewsResponse(
            mock_data, response_start_date, response_end_date
        )

        result = app.top_weekly_views("2023-07-01")

        dates = [
            "2023/07/01",
            "2023/07/02",
            "2023/07/03",
            "2023/07/04",
            "2023/07/05",
            "2023/07/06",
            "2023/07/07",
        ]
        mock_top_articles.assert_called_with(dates)
        mock_response.assert_called_with(
            mock_data, response_start_date, response_end_date
        )
        self.assertEqual(result, mock_response.return_value)

    def test_exceptions_caught(self):
        try:
            # Invalid date input
            app.top_weekly_views("07/01/2023")
            # No data available
            app.top_weekly_views("2003-07-01")
        except Exception:
            self.fail("top_weekly_views raised Exception unexpectedly")


class TopMonthlyViewsTest(unittest.TestCase):
    @patch("response.TopViewsResponse")
    @patch("wikipedia_client.top_articles")
    def test_get_top_articles(self, mock_top_articles, mock_response):
        mock_data = [
            {
                "items": [
                    {
                        "articles": [
                            {"article": "foo", "views": 4},
                            {"article": "bar", "views": 2},
                        ]
                    }
                ]
            }
        ]
        mock_top_articles.return_value = mock_data
        response_start_date = datetime(2023, 7, 1)
        response_end_date = datetime(2023, 7, 31)
        mock_response.return_value = response.TopViewsResponse(
            mock_data, response_start_date, response_end_date
        )

        result = app.top_monthly_views("July", "2023")

        dates = [
            "2023/07/01",
            "2023/07/02",
            "2023/07/03",
            "2023/07/04",
            "2023/07/05",
            "2023/07/06",
            "2023/07/07",
            "2023/07/08",
            "2023/07/09",
            "2023/07/10",
            "2023/07/11",
            "2023/07/12",
            "2023/07/13",
            "2023/07/14",
            "2023/07/15",
            "2023/07/16",
            "2023/07/17",
            "2023/07/18",
            "2023/07/19",
            "2023/07/20",
            "2023/07/21",
            "2023/07/22",
            "2023/07/23",
            "2023/07/24",
            "2023/07/25",
            "2023/07/26",
            "2023/07/27",
            "2023/07/28",
            "2023/07/29",
            "2023/07/30",
            "2023/07/31",
        ]
        mock_top_articles.assert_called_with(dates)
        mock_response.assert_called_with(
            mock_data, response_start_date, response_end_date
        )
        self.assertEqual(result, mock_response.return_value)

    def test_exceptions_caught(self):
        try:
            # Invalid month input
            app.top_monthly_views("Jul", "2023")
            # No data available
            app.top_monthly_views("July", "2003")
        except Exception:
            self.fail("top_monthly_views raised Exception unexpectedly")


class DayOfMonthWithMostViewsTest(unittest.TestCase):
    @patch("response.DateWithMostViewsResponse")
    @patch("wikipedia_client.views_per_article_by_day")
    def test_get_views_per_article_by_day(self, mock_views_by_day, mock_response):
        mock_data = [
            {"items": [{"timestamp": "2023070500", "views": 6}]},
            {"items": [{"timestamp": "2023070200", "views": 4}]},
        ]
        mock_views_by_day.return_value = mock_data
        mock_response.return_value = response.DateWithMostViewsResponse(
            mock_data, "foo"
        )

        result = app.day_of_month_with_most_views("foo", "July")

        dates = [
            "20230701",
            "20230702",
            "20230703",
            "20230704",
            "20230705",
            "20230706",
            "20230707",
            "20230708",
            "20230709",
            "20230710",
            "20230711",
            "20230712",
            "20230713",
            "20230714",
            "20230715",
            "20230716",
            "20230717",
            "20230718",
            "20230719",
            "20230720",
            "20230721",
            "20230722",
            "20230723",
            "20230724",
            "20230725",
            "20230726",
            "20230727",
            "20230728",
            "20230729",
            "20230730",
            "20230731",
        ]
        mock_views_by_day.assert_called_with("foo", dates, "daily")
        mock_response.assert_called_with(mock_data, "foo")
        self.assertEqual(result, mock_response.return_value)
        self.assertEqual(result.date, ["2023/07/05"])
        self.assertEqual(result.views, 6)

    def test_exceptions_caught(self):
        try:
            # Invalid article
            app.day_of_month_with_most_views("", "July")
            # Invalid month
            app.day_of_month_with_most_views("foo", "Jul")
            # No data available
            app.day_of_month_with_most_views("foo", "July", "2003")
        except Exception:
            self.fail("day_of_month_with_most_views raised Exception unexpectedly")


if __name__ == "__main__":
    unittest.main()
