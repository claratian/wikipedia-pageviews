from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import pageviews
import json
from datetime import datetime, date

app = Flask(__name__)
api = Api(app)


class ArticleViews(Resource):
    def get(self, granularity, article, date):
        if granularity.lower() == "weekly":
            result = pageviews.weekly_views_per_article(article, date)
            return json.dumps(result.__dict__), 200
        else:
        	result = pageviews.monthly_views_per_article(article, date)
        	return json.dumps(result.__dict__), 200

class TopViews(Resource):
	def get(self, granularity, date):
		if granularity.lower() == "weekly":
			pageviews.top_weekly_views(date)
		elif granularity.lower() == "monthly":
			pageviews.top_monthly_views(date)
		else:
			abort(400, message="Top views granularity must be either 'weekly' or 'monthly'")

class DayWithMostViews(Resource):
	def get(self, article, year_month):
		result = pageviews.day_of_month_with_most_views(article, year_month)
		return json.dumps(result.__dict__), 200

article_views_routes = ["/views/weekly/<article>/<int:year>/<month>/<int:day>",
    "/views/monthly/<article>/<int:year>/<int:month>"]

api.add_resource(ArticleViews, "/views/<granularity>/<article>/<date>")

top_articles_routes = ["/top/weekly/<year_month_day>",
	"/top/monthly/<year_month>"]

api.add_resource(TopViews, *top_articles_routes)

api.add_resource(DayWithMostViews, "/views/top-day/<article>/<year_month>")

@app.route("/")
def index():
    return "Wikimedia Pageviews Wrapper"


if __name__ == "__main__":
    app.run(port=8000, debug=True)
