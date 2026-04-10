from datetime import date, datetime, time, timedelta


def get_date(timedelta_days: int) -> date:
    """
    Return a date offset from today.

    Parameters:
        timedelta_days (int): Number of days to subtract from current date.

    Returns:
        date: Computed date.
    """

    today = date.today()
    result = today - timedelta(days=timedelta_days)
    return result


def get_date_from_string(date_str: str) -> date:
    """
    Parse an ISO formatted string into a date object.

    Parameters:
        date_str (str): ISO date string (YYYY-MM-DD).

    Returns:
        date: Parsed date object.

    Raises:
        ValueError: If the input string is not a valid ISO date.
    """

    try:
        result = datetime.fromisoformat(date_str).date()
        return result
    except ValueError:
        raise


def get_iso_date_from_date(old_date: date) -> str:
    """
    Convert a date object to an ISO 8601 datetime string at UTC midnight.

    Parameters:
        old_date (date): Input date.

    Returns:
        str: ISO formatted datetime string with 'Z' suffix.
    """

    try:
        dt = datetime.combine(old_date, time.min)
        formatted_date = dt.isoformat() + "Z"
        return formatted_date
    except ValueError:
        raise
