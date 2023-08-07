from context import app, wikipedia_client

import unittest
import mock
from mock import patch

class AppTestSuite(unittest.TestCase):

	def test_weekly_views_per_article(self):
		# mock that wikipedia_client.views_per_article is called
		with patch.object(wikipedia_client.views_per_article, 'views_per_article') as mock:
			result = app.weekly_views_per_article('Barbie (film)', '7/1/2023')
			mock.assert_called_with('Barbie (film)', '20230701', '20230707', 'daily')

if __name__ == "__main__":
    unittest.main()
