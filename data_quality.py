"""Conservative market-data quality checks."""
from datetime import datetime, timezone


def check_bar_quality(timestamp, *, now=None, max_age_seconds=6.0,
                      price=None, open_price=None, high=None, low=None, volume=None):
    """Validate timestamp freshness and basic OHLCV consistency.

    A clean result is necessary but not sufficient to prove feed accuracy.
    """
    now = now or datetime.now(timezone.utc)
    problems = []
    if timestamp is None or not isinstance(timestamp, datetime):
        problems.append("missing_or_invalid_timestamp")
    elif timestamp.tzinfo is None or timestamp.utcoffset() is None:
        problems.append("timestamp_missing_timezone")
    elif now.tzinfo is None or now.utcoffset() is None:
        problems.append("clock_missing_timezone")
    else:
        age = (now - timestamp).total_seconds()
        if age < -1.0:
            problems.append("timestamp_in_future")
        elif age > max_age_seconds:
            problems.append("stale_bar")

    for name, value in {"price": price, "open": open_price, "high": high, "low": low}.items():
        if value is not None:
            try:
                if float(value) <= 0:
                    problems.append(f"invalid_{name}")
            except (TypeError, ValueError):
                problems.append(f"invalid_{name}")
    try:
        if high is not None and low is not None and float(high) < float(low):
            problems.append("high_below_low")
        if high is not None and price is not None and float(price) > float(high):
            problems.append("price_above_high")
        if low is not None and price is not None and float(price) < float(low):
            problems.append("price_below_low")
        if volume is not None and float(volume) < 0:
            problems.append("negative_volume")
    except (TypeError, ValueError):
        problems.append("invalid_ohlcv_value")

    problems = list(dict.fromkeys(problems))
    age_seconds = None
    if (isinstance(timestamp, datetime) and timestamp.tzinfo is not None
            and timestamp.utcoffset() is not None and now.tzinfo is not None
            and now.utcoffset() is not None):
        age_seconds = round((now - timestamp).total_seconds(), 3)
    return {"ok": not problems, "age_seconds": age_seconds,
            "problems": problems, "actionable": not problems}


def can_issue_signal(quality_result):
    """Fail closed unless the result explicitly passes all quality checks."""
    return (isinstance(quality_result, dict)
            and quality_result.get("ok") is True
            and quality_result.get("actionable") is True
            and not quality_result.get("problems"))
