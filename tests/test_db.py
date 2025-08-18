import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import date, datetime, time

# Ensure the repository root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Mock supabase module before importing db
supabase_mock = types.ModuleType("supabase")
supabase_mock.create_client = MagicMock(return_value=MagicMock())
supabase_mock.Client = MagicMock()
sys.modules["supabase"] = supabase_mock

import db


def test_get_date_range_today():
    fixed_today = date(2023, 9, 15)

    class FixedDate(date):
        @classmethod
        def today(cls):
            return fixed_today

    with patch('db.date', FixedDate):
        start, end = db.get_date_range('today')

    assert start == datetime.combine(fixed_today, time.min)
    assert end == datetime.combine(fixed_today, time.max)


def test_get_date_range_last_week():
    fixed_today = date(2023, 9, 15)

    class FixedDate(date):
        @classmethod
        def today(cls):
            return fixed_today

    with patch('db.date', FixedDate):
        start, end = db.get_date_range('last_week')

    expected_start = datetime.combine(date(2023, 9, 4), time.min)
    expected_end = datetime.combine(date(2023, 9, 10), time.max)
    assert start == expected_start
    assert end == expected_end


def test_get_date_range_last_month():
    fixed_today = date(2023, 9, 15)

    class FixedDate(date):
        @classmethod
        def today(cls):
            return fixed_today

    with patch('db.date', FixedDate):
        start, end = db.get_date_range('last_month')

    expected_start = datetime.combine(date(2023, 8, 1), time.min)
    expected_end = datetime.combine(date(2023, 8, 31), time.max)
    assert start == expected_start
    assert end == expected_end
