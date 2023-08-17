from context import wikipedia_client
from context import errors

import unittest
import mock
from errors import ZeroOrNotLoadedDataException, ThrottlingException
from mock import patch, call

HEADERS = wikipedia_client.HEADERS


class WikipediaClientTest(unittest.TestCase):
    @patch("requests.get")
    def test_top_articles(self, mock_requests):
        api_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date}"
        dates = [
            "2023/07/01",
            "2023/07/02",
            "2023/07/03",
            "2023/07/04",
            "2023/07/05",
            "2023/07/06",
            "2023/07/07",
        ]

        wikipedia_client.top_articles(dates)

        calls = [call(api_url.format(date=date), headers=HEADERS) for date in dates]
        mock_requests.assert_has_calls(calls, any_order=True)

    @patch("requests.get")
    def test_views_per_article_by_day(self, mock_requests):
        article = "foo"
        dates = ["20230701", "20230702", "20230703"]
        api_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/daily/{start}/{end}"
        wikipedia_client.views_per_article_by_day(article, dates, "daily")

        calls = [
            call(api_url.format(article=article, start=date, end=date), headers=HEADERS)
            for date in dates
        ]
        mock_requests.assert_has_calls(calls, any_order=True)

    @patch("requests.get")
    def test_views_per_article(self, mock_requests):
        article = "foo"
        start_date = "20230701"
        end_date = "20230703"
        api_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/daily/{start}/{end}"
        wikipedia_client.views_per_article(article, start_date, end_date, "daily")

        mock_requests.assert_called_with(
            api_url.format(article=article, start=start_date, end=end_date),
            headers=HEADERS,
        )

    def test_zero_data_exception(self):
        top_articles_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/{date}"
        per_article_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/all-agents/{article}/daily/{start}/{end}"
        # Exception should be thrown if any dates are invalid
        invalid_top_dates = ["2003/07/01", "2003/07/02", "2023/07/03"]
        invalid_per_article_dates = ["20030701", "20030731"]

        with self.assertRaises(Exception) as context:
            wikipedia_client.top_articles(invalid_top_dates)
        self.assertEqual(len(context.exception.dates), 2)

        with self.assertRaises(Exception) as context:
            wikipedia_client.views_per_article_by_day(
                "foo", invalid_per_article_dates, "daily"
            )
        self.assertEqual(len(context.exception.dates), 2)

        self.assertRaises(
            ZeroOrNotLoadedDataException,
            lambda: wikipedia_client.views_per_article(
                "foo", "20030701", "20030731", "monthly"
            ),
        )

    @patch("requests.get")
    def test_throttling_exception(self, mock_requests):
        # Should raise throttling exception immediately rather than returning list of errors
        mock_requests.return_value.status_code = 429
        self.assertRaises(
            ThrottlingException, lambda: wikipedia_client.top_articles(["2023/07/01"])
        )
        self.assertRaises(
            ThrottlingException,
            lambda: wikipedia_client.views_per_article_by_day(
                "foo", ["20230707"], "daily"
            ),
        )
        self.assertRaises(
            ThrottlingException,
            lambda: wikipedia_client.views_per_article(
                "foo", "20230701", "20230731", "monthly"
            ),
        )


if __name__ == "__main__":
    unittest.main()
