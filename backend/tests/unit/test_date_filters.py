"""
Unit tests for date filtering utilities
T160-T162: Test date classification functions
"""

import pytest
from datetime import datetime, timedelta
from src.study_helper.utils.date_filters import is_today, is_this_week, is_upcoming


class TestDateFilters:
    """Test date filtering utilities for task views"""

    def test_is_today(self):
        """T160 [RED]: Test is_today() returns True for today's date"""
        today = datetime.now().date()
        assert is_today(today) is True
        
        yesterday = today - timedelta(days=1)
        assert is_today(yesterday) is False
        
        tomorrow = today + timedelta(days=1)
        assert is_today(tomorrow) is False

    def test_is_this_week_includes_today(self):
        """T161 [RED]: Test is_this_week() returns True for today through next 7 days"""
        today = datetime.now().date()
        
        # Today should be included in "this week"
        assert is_this_week(today) is True
        
        # Tomorrow through 7 days from now should be in "this week"
        for days in range(1, 8):
            future_date = today + timedelta(days=days)
            assert is_this_week(future_date) is True, f"Day {days} should be in this week"
        
        # 8 days from now should NOT be in "this week"
        future_date = today + timedelta(days=8)
        assert is_this_week(future_date) is False
        
        # Yesterday should NOT be in "this week"
        yesterday = today - timedelta(days=1)
        assert is_this_week(yesterday) is False

    def test_is_upcoming_beyond_7_days(self):
        """T162 [RED]: Test is_upcoming() returns True for dates beyond this week"""
        today = datetime.now().date()
        
        # Today and this week should NOT be "upcoming"
        assert is_upcoming(today) is False
        
        for days in range(1, 8):
            future_date = today + timedelta(days=days)
            assert is_upcoming(future_date) is False
        
        # 8+ days from now should be "upcoming"
        for days in range(8, 15):
            future_date = today + timedelta(days=days)
            assert is_upcoming(future_date) is True, f"Day {days} should be upcoming"
        
        # Past dates should NOT be "upcoming"
        yesterday = today - timedelta(days=1)
        assert is_upcoming(yesterday) is False

    def test_none_date_handling(self):
        """Test functions handle None dates gracefully"""
        assert is_today(None) is False
        assert is_this_week(None) is False
        assert is_upcoming(None) is False

    def test_datetime_conversion(self):
        """Test functions work with datetime objects (not just date)"""
        now = datetime.now()
        assert is_today(now) is True
        assert is_this_week(now) is True
        assert is_upcoming(now) is False
