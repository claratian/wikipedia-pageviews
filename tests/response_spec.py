import unittest

from context import response

class TopViewsResponseTest(unittest.TestCase):
	def test_parse_json(self):
		day1 = {"items":[{"articles": [{"article": "foo", "views": 1}, {"article": "bar", "views": 2}]}]}
		day2 = {"items":[{"articles": [{"article": "foo", "views": 3}, {"article": "bar", "views": 4}]}]}
		result = response.TopViewsResponse([day1, day2])
		article_views = [{"rank": 1, "article": "bar", "views": 6}, {"rank": 2, "article": "foo", "views": 4}]
		self.assertEqual(result.article_views, article_views)

	def test_exception(self):
		day1 = {"items":[{"articles": [{"article": "foo", "views": 1}, {"article": "bar", "views": 2}]}]}
		day2 = {"foo": [{"articles": [{"article": "foo", "views": 3}, {"article": "bar", "views": 4}]}]}
		self.assertRaises(response.ParseResponseException, lambda: response.TopViewsResponse([day1, day2]))

class DateWithMostViewsResponseTest(unittest.TestCase):
	def test_parse_json(self):
		day1 = {"items":[{"article": "foo", "timestamp": "2023070700", "views": 1}]}
		day2 = {"items":[{"article": "foo", "timestamp": "2023070800", "views": 2}]}
		result = response.DateWithMostViewsResponse([day1, day2], "foo")
		dates = ["07/08/2023"]
		
		self.assertEqual(result.date, dates)
		self.assertEqual(result.views, 2)
		self.assertEqual(result.article, "foo")

	def test_multiple_dates(self):
		day1 = {"items":[{"article": "foo", "timestamp": "2023070700", "views": 1}]}
		day2 = {"items":[{"article": "foo", "timestamp": "2023070800", "views": 2}]}
		day3 = {"items":[{"article": "foo", "timestamp": "2023070900", "views": 2}]}
		result = response.DateWithMostViewsResponse([day1, day2, day3], "foo")
		dates = ["07/08/2023", "07/09/2023"]
		
		self.assertEqual(result.date, dates)
		self.assertEqual(result.views, 2)
		self.assertEqual(result.article, "foo")

	def test_exception(self):
		day1 = {"items":[{"article": "foo", "timestamp": "2023070700", "views": 1}]}
		day2 = {"items":[{"article": "foo", "timestamp": "2023070800", "bar": 2}]}
		self.assertRaises(response.ParseResponseException, lambda: response.DateWithMostViewsResponse([day1, day2], "foo"))

class ArticleViewsResponseTest(unittest.TestCase):
	def test_init_response(self):
		data = {"items": [{"article": "foo", "views": 10}, {"article": "foo", "views": 12}]}
		result = response.ArticleViewsResponse(data, "foo", "07/01/2023", "07/07/2023")
		self.assertEqual(result.views, 22)
		self.assertEqual(result.article, "foo")
		self.assertEqual(result.start_date, "07/01/2023")
		self.assertEqual(result.end_date, "07/07/2023")

	def test_exception(self):
		data = {"items": [{"article": "foo", "views": 10}, {"article": "foo", "v": 12}]}
		self.assertRaises(response.ParseResponseException, lambda: response.ArticleViewsResponse(data, "foo", "07/01/2023", "07/07/2023"))

if __name__ == "__main__":
	unittest.main()