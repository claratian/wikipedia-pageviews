# WikiMedia PageViews Wrapper

This is a wrapper for the [WikiMedia PageViews API](https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews) built on top of the `requests` library.


The following user functions are supported:
- Retrieve a list of the most viewed articles for a week or a month
- For any given article, be able to get the view count of that specific article for a week or a
month
- Retrieve the day of the month where an article got the most page views

## Run Instructions
Note: This project requires Python 3 to be installed first. For help doing this, see [this resource](https://realpython.com/installing-python/).

If needed, install the requests library with `sudo pip3 install requests`.
Install any other missing required libraries using `pip3 install -r requirements.txt`

Clone this repo and open a shell at the `src` directory of the project.
To test running the functions in `app.py`, run 
```
>>> python3
>>> import app
```
Methods can then be called as such:
`app.<method_name>` or `<variable_name> = app.<method_name>` to be able to access the attributes on each response object (defined in `response.py`) that is returned for each function. To have the option of a simpler user experience, an output message is also printed for each method call. To not see a printed output, one can comment out the print statements above each `return result` in `app.py`.
### Get view count of a specific article for a week or month

The methods below return a `response.ArticleViewsResponse` object with attributes
- start_date
- end_date
- views
- article

Additional documentation on these attributes can be seen in `response.py`.
```
>>> result = app.weekly_views_per_article("Barbie (film)", "2023/07/01")
Page views for Barbie (film) between 2023/07/01 and 2023/07/07: 394276

>>> result.start_date
'2023/07/01'
>>> result.end_date
'2023/07/07'
>>> result.views
394276
>>> result.article
'Barbie (film)'

>>> app.monthly_views_per_article("Barbie (film)", "July", "2023")
Page views for Barbie (film) during July 2023: 9561981

<response.ArticleViewsResponse object at 0x104a64610>

# If a year is not provided, the current year is used by default
>>> app.monthly_views_per_article("Barbie (film)", "July")
Page views for Barbie (film) during July 2023: 9561981

<response.ArticleViewsResponse object at 0x105499990>
```
### Retrieve the day of the month where an article got the most page views

The method below returns a `response.DateWithMostViewsResponse` object with attributes
- date - this is returned as a list in case there are multiple dates tied for the most views
- views
- article

Additional documentation on these attributes can be found in `response.py`.
```
>>> result = app.day_of_month_with_most_views("Barbie (film)", "July")
The day(s) of July where Barbie (film) was most viewed was  ['2023/07/22'], with 929915 views

>>> result.date
['2023/07/22']
>>> result.views
929915
>>> result.article
'Barbie (film)'

```
If there happen to be multiple dates tied for the most views in a month for a given article, all of them will be returned in `result.date` and displayed in the output.

### Get a list of the most viewed articles for a week or month
The following methods return a `response.TopViewsResponse` object with attributes
- article_views
- start_date
- end_date

Additional documentation on these attributes can be found in `response.py`
```
>>> app.top_weekly_views("2023/07/01")
Top page views for week of 2023/07/01-2023/07/07:
[{'rank': 1, 'article': 'Main_Page', 'views': 32339402}, {'rank': 2, 'article': 'Special:Search', 'views': 8251033}, {'rank': 3, 'article': 'The_Idol_(TV_series)', 'views': 3031374}, {'rank': 4, 'article': 'Indiana_Jones_and_the_Dial_of_Destiny', 'views': 1671032}, {'rank': 5, 'article': 'Wikipedia:Featured_pictures', 'views': 1457503}, <rest of response omitted for readability>...]

<response.TopViewsResponse object at 0x104a22d50>

# Note: if the year is not provided, the current year is used by default
>>> result = app.top_monthly_views("August", "2022")
Top page views for August 2022:
[{'rank': 1, 'article': 'Main_Page', 'views': 142936116}, {'rank': 2, 'article': 'Special:Search', 'views': 39757512}, {'rank': 3, 'article': 'Anne_Heche', 'views': 10257269}, {'rank': 4, 'article': 'Olivia_Newton-John', 'views': 5662700}, <omitted for readability> ...]

>>> result.article_views
[{'rank': 1, 'article': 'Main_Page', 'views': 142936116}, {'rank': 2, 'article': 'Special:Search', 'views': 39757512}, {'rank': 3, 'article': 'Anne_Heche', 'views': 10257269}, {'rank': 4, 'article': 'Olivia_Newton-John', 'views': 5662700}, <rest omitted>...]
>>> result.start_date
'2022/08/01'
>>> result.end_date
'2022/08/31'

```
### Usage Tips

- For methods that require input dates, the date should be formatted as a string in one of the following formats: yyyy/mm/dd, yyyy/m/d, yyyy-mm-dd, or yyyy-m-d.
- When providing a month name to query for, the full month name should be used (e.g. January, and not Jan or "1")
- Month or week ranges before 10/10/15 (as of the time this document is being written) or after the current date will not have page view data available.

### Design decisions/assumptions
- An input week can start from any date and includes that date and the following 6 days, whereas an input month must be a specific calendar month (August, July, etc instead of July 5 - August 5).
- When querying for page view data for a month or week, if Wikimedia does not successfully return data for any dates in that month or week, no results will be returned since missing data for any day in the requested range will compromise the accuracy of the answer.
- Input date allowed formats are limited for ease of input validation and for consistency with date formats on response objects.
- Any exceptions thrown are swallowed at the `app.py` level for a visually cleaner user experience when building and running this project (although error messages are still printed to be informative), but in a production setting, the exception should probably be returned to the client, and the print statements would be error logs isntead. 
- Each public method in `app.py` returns some type of `response` object to mimic how a wrapper API might respond to requests realistically, but the inputs are not 'request' objects to make running the project locally a bit more convenient.
- For a queried date range where some/all dates are missing data, the returned Exception contains information about all dates with missing data so the client/user can more easily fix their request in one try.

### Running tests

To run tests, navigate to the tests directory of the project and run `python3 <name of test>.py` - for example:
```
python3 wikipedia_client_test.py
.....
Ran 5 tests in 0.744s

OK

```
