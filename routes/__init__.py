"""Input guards shared by the pages that take user choices.

Anything arriving in request.args is text typed by whoever made the request, so
it is checked against the list of values the database actually offers before it
reaches a query. An unrecognised value falls back to a sensible default instead
of raising, which keeps a hand-edited URL from producing an error page.
"""


def choose(value, allowed, fallback):
    return value if value in allowed else fallback


def choose_int(value, allowed, fallback):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return fallback
    return number if number in allowed else fallback
