class ZeroOrNotLoadedDataException(Exception):
    """
    Raised for 404 Error from Wikimedia API

    Either there are 0 pageviews for the given project, timespan and filters
    specified in the query, or the requested data (like a request for the current day)
    has not yet been loaded into the API's database yet.
    https://wikitech.wikimedia.org/wiki/Analytics/PageviewAPI#Gotchas

    @param date: date for which there was 0 views or no data
    @param date_range: start and end date for which there was 0 views or no data
    (present only for views per article queries)
    """

    def __init__(self, date):
        self.date = date

    def __str__(self):
        if isinstance(self.date, list):
            return "0 pageviews or data not available for date range {dates}".format(
                dates=str(self.date)
            )
        else:
            return "0 pageviews or data not available for date {date}".format(
                date=str(self.date)
            )


class ThrottlingException(Exception):
    """
    Raised for 429 Error from Wikimedia API

    Client has made too many requests and it is being throttled.
    This will happen if the storage cannot keep up with the request ratio from a given IP
    https://wikitech.wikimedia.org/wiki/Analytics/PageviewAPI#Gotchas
    """

    def __str__(self):
        return "Too many requests made"


class InvalidInputError(Exception):
    """
    Raised for invalid input provided to methods in app.py
    """

    def __init__(self, message):
        self.message = message


class ParseResponseException(Exception):
    """
    Raised when the response from the Wikimedia API is not in the expected format
    and cannot be parsed
    """

    def __init__(self, error):
        self.message = "Unexpected response format: {err}".format(err=error)
