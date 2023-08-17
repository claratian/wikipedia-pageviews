from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import pageviews
import json
from datetime import datetime, date
import errors

app = Flask(__name__)
api = Api(app)


class ArticleViews(Resource):
	def get(self, granularity, article, date):
		"""
		Parameters:
		- granularity (str): The granularity of the article views data. Can be either 'weekly' or
			'monthly' (for views of the article in a week or month)
		- article (str): The name of the article to get views for (case sensitive). Spaces should 
			be represented as underscores (e.g. the article Barbie (film) should be represented as 
			Barbie_(film))
		- date (str): An ISO 8601 formatted date string with the format YYYY-MM-DD for a weekly
			granularity or YYYY-MM for a monthly granularity. For a weekly request, the date
			indicates the day from which the week starts, and for monthly requests, the date
			indicates the month and year to get article views for

		Returns:
		A json formatted ArticleViewsResponse object with the following attributes
		- article (str): the name of the article requested (case-sensitive)
		- views (int): the number of views the article received in the requested period
		- start_date (str): the date from which the article view data starts in ISO 8601 format
		- end_date (str): the date up to and including which the article view data ends in ISO
			8601 format
		"""
		try:
			result = pageviews.views_per_article(granularity, article, date)
			return result.__dict__, 200
		except errors.InvalidInputException as i:
			return str(i), 400
		except errors.ZeroOrNotLoadedDataException as z:
			return str(z), 404
		except errors.ThrottlingException as t:
			return str(t), 429


class TopViews(Resource):
	def get(self, granularity, date):
		"""
		Parameters:
		- granularity (str): The granularity of the top views data. Can be either 'weekly' or
			'monthly' (for weekly or monthly top viewed articles)
		- date (str): An ISO 8601 formatted date string with the format YYYY-MM-DD for a weekly
			granularity or YYYY-MM for a monthly granularity. For a weekly request, the date
			indicates the day from which the week starts, and for monthly requests, the date
			indicates the month and year to get top viewed articles for

		Returns:
		A json formatted TopViewsResponse object with the following attributes:
		- article_views (list<dict>): a list of hashes describing cumulative top article views
			for the week or the month provided ordered from most to least views with the format

			[
					{
							'rank' (int): <ranking based on total views>,
							'article' (str): <article name>,
							'article_views' (int): <total cumulative views>
					},
					...
			]
		- start_date (str): the date from which the article views are counted,
			represented in ISO 8601 format
		- end_date (str): the date up to and including which article views
			are counted, represented in ISO 8601 format
		"""
		try:
			result = pageviews.top_views(granularity, date)
			return result.__dict__, 200
		except errors.InvalidInputException as i:
			return str(i), 400
		except errors.ZeroOrNotLoadedDataException as z:
			return str(z), 404
		except errors.ThrottlingException as t:
			return str(t), 429


class DayWithMostViews(Resource):
	def get(self, article, year_month):
		"""
		Parameters:
		- article (str): the name of the article (case sensitive). Spaces should be represented as 
			underscores (e.g. the article Barbie (film) should be represented as Barbie_(film))
		- year_month (str): An ISO 8601 formatted date string with the format YYYY-MM

		Returns:
		A json formatted DateWithMostViewsResponse object with attributes
		- date (list<str>): a list of ISO 8601 dates representing the date (or dates if
			multiple days are tied) the article received the most views in the month requested
		- views (int): the number of views for the article on the returned date(s)
		- article (str): the name of the requested article
		"""
		try:
			result = pageviews.day_of_month_with_most_views(article, year_month)
			return result.__dict__, 200
		except errors.InvalidInputException as i:
			return str(i), 400
		except errors.ZeroOrNotLoadedDataException as z:
			return str(z), 404
		except errors.ThrottlingException as t:
			return str(t), 429


api.add_resource(ArticleViews, "/views/<granularity>/<article>/<date>")

api.add_resource(TopViews, "/top/<granularity>/<date>")

api.add_resource(DayWithMostViews, "/views/top-day/<article>/<year_month>")


@app.route("/")
def index():
	return "Wikimedia Pageviews Wrapper"


if __name__ == "__main__":
	app.run(port=8000, debug=True)
