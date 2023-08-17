
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
To run the server locally, from the `src` directory, run `python3 main.py`. To avoid seeing debug output, set `debug=False` on the `app.run` call on line 124.
```
>>> python3 main.py
 * Serving Flask app 'main'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 382-815-555
```
Visit the localhost address above (`http://127.0.0.1:8000`) in a web browser.
### Get view count of a specific article for a week or month

Path: `/views/<granularity>/<article_name>/<date>`

Some examples:

http://127.0.0.1:8000/views/monthly/NewJeans/2022-12

Response:
```
{
    "views": 110966,
    "article": "NewJeans",
    "start_date": "2022-12-01",
    "end_date": "2022-12-31"
}
```

http://127.0.0.1:8000/views/weekly/NewJeans/2023-08-01

Response:
```
{
    "views": 75121,
    "article": "NewJeans",
    "start_date": "2023-08-01",
    "end_date": "2023-08-07"
}
```

The granularity should be either `weekly` to get weekly views for an article or `monthly` to get monthly views for an article.

The article name should be case sensitive (for example, searching for article views on `newjeans` will not return the same result as `NewJeans`). Any spaces in the article name should be represented with an underscore (e.g. `Barbie_(film)`). 
Note: special characters such as accents on letters and apostrophes will need to be [URL encoded](https://documentation.n-able.com/N-central/userguide/Content/Further_Reading/API_Level_Integration/API_Integration_URLEncoding.html) (for example, http://127.0.0.1:8000/views/monthly/Prisoner%27s_dilemma/2022-12).

Finally, the date should be in [ISO 8601](https://www.iso.org/iso-8601-date-and-time-format.html) format: YYYY-MM-DD if the granularity is weekly and YYYY-MM if the granularity is monthly. 
Note: month or week ranges before 2015-10-10 (as of the time this document is being written) or after the current date will not have page view data available.


### Retrieve the day of the month where an article got the most page views

Path: `/views/top-day/<article_name>/<date>`

The same notes on the how the article and date parameters should be formatted apply from the previous section, but the date should always be in YYYY-MM format as the requested time frame will always be a month.

Example:
http://127.0.0.1:8000/views/top-day/NewJeans/2022-12

Response:
```
{
    "date": [
        "2022-12-20"
    ],
    "views": 8128,
    "article": "NewJeans"
}
```


If there happen to be multiple dates tied for the most views in a month for a given article, all of them will be returned in the `"date"` attribute of the response.

### Get a list of the most viewed articles for a week or month

Path: `/top/<granularity>/<date>`

Just like getting the view count of a specific article for a week or month,
the granularity should be either `weekly` to get weekly views for an article or `monthly` to get monthly views for an article.

The date should also be in ISO 8601 format: YYYY-MM-DD if the granularity is weekly and YYYY-MM if the granularity is monthly.

Some examples:

Request: http://127.0.0.1:8000/top/monthly/2023-04

Partial response (rest ommitted for readability)
```
{
    "start_date": "2023-04-01",
    "end_date": "2023-04-30",
    "article_views": [
        {
            "rank": 1,
            "article": "Main_Page",
            "views": 138416489
        },
        {
            "rank": 2,
            "article": "Special:Search",
            "views": 39194421
        },
        {
            "rank": 3,
            "article": "Indian_Premier_League",
            "views": 8512012
        }, ...
```

Request: 
http://127.0.0.1:8000/top/weekly/2023-04-01

Partial response (rest ommitted for readability)
```
{
    "start_date": "2023-04-01",
    "end_date": "2023-04-07",
    "article_views": [
        {
            "rank": 1,
            "article": "Main_Page",
            "views": 31868635
        },
        {
            "rank": 2,
            "article": "Special:Search",
            "views": 8961977
        },
        {
            "rank": 3,
            "article": "Indian_Premier_League",
            "views": 3050902
        },
        {
            "rank": 4,
            "article": "WrestleMania_39",
            "views": 2602769
        },
        ...
```


### Design decisions/assumptions
- An input week can start from any date and includes that date and the following 6 days, whereas an input month must be a specific calendar month (2023-08, 2023-07, etc instead of 2023-07-05 through 2023-08-05).
- When querying for page view data for a month or week, if Wikimedia does not successfully return data for any dates in that month or week, no results will be returned since missing data for any day in the requested range will compromise the accuracy of the answer.
- For a queried date range where some or all dates are missing data, the returned Exception contains information about all requested dates that returned no/missing data so the client can more easily fix their request in one try, although for the `/views` endpoint, because only one request (with a start and end date) is sent to the Wikimedia server, only the start and end date of the requested time will be returned as having missing data.

### Running tests

To run tests, navigate to the tests directory of the project and run `python3 <name of test>.py` - for example:
```
python3 wikipedia_client_test.py
.....
Ran 5 tests in 0.744s

OK

```
Note: To run `main_test.py`, the server must be running locally first (run `python3 main.py` from the src directory and run `python3 main_test.py` from the tests directory in a separate tab).