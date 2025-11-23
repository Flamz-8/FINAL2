"""
Date filtering utilities for task views
T163-T166: Classify dates as today, this week, or upcoming
"""

from datetime import datetime, date, timedelta
from typing import Union, Optional


def is_today(target_date: Optional[Union[date, datetime]]) -> bool:
    """
    T163 [GREEN]: Check if date is today
    
    Args:
        target_date: Date to check (can be date or datetime)
        
    Returns:
        True if date is today, False otherwise
    """
    if target_date is None:
        return False
    
    # Convert datetime to date if needed
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    today = datetime.now().date()
    return target_date == today


def is_this_week(target_date: Optional[Union[date, datetime]]) -> bool:
    """
    T164 [GREEN]: Check if date is within this week (today through next 7 days)
    
    Per Clarification #4: "This Week" = today + next 7 days (8 days total)
    
    Args:
        target_date: Date to check
        
    Returns:
        True if date is today through 7 days from now, False otherwise
    """
    if target_date is None:
        return False
    
    # Convert datetime to date if needed
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    return today <= target_date <= week_end


def is_upcoming(target_date: Optional[Union[date, datetime]]) -> bool:
    """
    T165 [GREEN]: Check if date is upcoming (beyond this week)
    
    "Upcoming" = more than 7 days from now
    
    Args:
        target_date: Date to check
        
    Returns:
        True if date is more than 7 days from now, False otherwise
    """
    if target_date is None:
        return False
    
    # Convert datetime to date if needed
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    return target_date > week_end


def get_date_category(target_date: Optional[Union[date, datetime]]) -> str:
    """
    T166 [REFACTOR]: Categorize date into today/week/upcoming/overdue
    
    Args:
        target_date: Date to categorize
        
    Returns:
        Category: 'overdue', 'today', 'week', 'upcoming', or 'no_due_date'
    """
    if target_date is None:
        return 'no_due_date'
    
    # Convert datetime to date if needed
    if isinstance(target_date, datetime):
        target_date = target_date.date()
    
    today = datetime.now().date()
    
    # Check if overdue
    if target_date < today:
        return 'overdue'
    
    # Check categories in order
    if is_today(target_date):
        return 'today'
    elif is_this_week(target_date):
        return 'week'
    else:
        return 'upcoming'
