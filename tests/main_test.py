import requests
import json
import unittest

BASE_URL = "http://127.0.0.1:8000/"


class MainTest(unittest.TestCase):
    def test_get_top_weekly(self):
        res = requests.get(BASE_URL + "/top/weekly/2023-07-06")
        self.assertEqual(res.status_code, 200)
        snapshot = open("snapshots/top_weekly_20230706.json")
        self.assertEqual(
            res.json(), json.load(snapshot)
        )
        snapshot.close()

    def test_get_top_monthly(self):
        res = requests.get(BASE_URL + "/top/monthly/2023-06")
        self.assertEqual(res.status_code, 200)
        snapshot = open("snapshots/top_monthly_202306.json")
        self.assertEqual(
            res.json(), json.load(snapshot)
        )
        snapshot.close()

    def test_weekly_article_views(self):
        res = requests.get(BASE_URL + "/views/weekly/NewJeans/2023-08-04")
        self.assertEqual(res.status_code, 200)
        snapshot = open("snapshots/newjeans_views_20230804.json")
        self.assertEqual(
            res.json(), json.load(snapshot)
        )
        snapshot.close()

    def test_monthly_article_views(self):
        res = requests.get(BASE_URL + "/views/monthly/NewJeans/2023-06")
        self.assertEqual(res.status_code, 200)
        snapshot = open("snapshots/newjeans_views_202306.json")
        self.assertEqual(
            res.json(), json.load(snapshot)
        )
        snapshot.close()

    def test_top_views_day(self):
        res = requests.get(BASE_URL + "/views/top-day/NewJeans/2023-07")
        self.assertEqual(res.status_code, 200)
        snapshot = open("snapshots/top_day_newjeans_202307.json")
        self.assertEqual(
            res.json(), json.load(snapshot)
        )
        snapshot.close()

    def test_invalid_input(self):
        res = requests.get(BASE_URL + "/top/weekly/2023-07")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.json(),
            "Year, month, and day must be in valid ISO 8601 format (yyyy-mm-dd).",
        )

    def test_no_data(self):
        res = requests.get(BASE_URL + "/top/weekly/2007-07-05")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(
            res.json(),
            "0 pageviews or data not available for date range ['2007/07/05', '2007/07/06', '2007/07/07', '2007/07/08', '2007/07/09', '2007/07/10', '2007/07/11']",
        )

    def test_invalid_parameters(self):
    	res = requests.get(BASE_URL + "/views/top-day/NewJeans/202307")
    	self.assertEqual(res.status_code, 400)
    	self.assertEqual(
    		res.json(),
    		"Year and month must be in valid ISO 8601 format (yyyy-mm).",
    	)

    def test_invalid_url(self):
        res = requests.get(BASE_URL + "/top/weekly/2023-07-06/invalid")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
