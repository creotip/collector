import pytest

from collector.helpers import is_post_date_in_timespan


@pytest.mark.parametrize(
    "days,post_date,expected",
    [
        (10 / (24 * 60), "30s", True),  # 10 minutes
        (10 / (24 * 60), "5m", True),
        (10 / (24 * 60), "15m", False),
        (10 / (24 * 60), "1h", False),
        (1 / 24, "10m", True),  # 1 hour
        (1 / 24, "30m", True),
        (1 / 24, "1h", True),
        (1 / 24, "2h", False),
        (1, "12h", True),  # 24 hours
        (1, "18h", True),
        (1, "1d", True),
        (1, "2d", False),
        (1, "4s", True),  # 1 day, redundant with 24 hours but kept for clarity
        (1, "4m", True),
        (1, "4h", True),
        (1, "4d", False),
        (5, "2h", True),  # 5 days
        (5, "1d", True),
        (5, "3d", True),
        (5, "5d", True),
        (5, "7d", False),
        (30, "4s", True),  # 30 days
        (30, "4m", True),
        (30, "4h", True),
        (30, "4d", True),
        (30, "3w", True),
        (30, "3mo", False),
        (365, "4s", True),  # 365 days
        (365, "4m", True),
        (365, "4h", True),
        (365, "4d", True),
        (365, "3w", True),
    ],
)
def test_is_post_date_in_timespan(days, post_date, expected):
    assert is_post_date_in_timespan(post_date, days) == expected
