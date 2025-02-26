"""
Helper functions for the Business Game.
"""
import json
from datetime import datetime
from typing import Any, Dict


def format_currency(value: float, precision: int = 2, include_symbol: bool = True) -> str:
    """
    Format a value as currency.
    
    Args:
        value: The value to format
        precision: The number of decimal places
        include_symbol: Whether to include the currency symbol
        
    Returns:
        The formatted currency string
    """
    if include_symbol:
        return f"${value:.{precision}f}"
    else:
        return f"{value:.{precision}f}"


def format_percentage(value: float, precision: int = 1) -> str:
    """
    Format a value as a percentage.
    
    Args:
        value: The value to format (as a decimal)
        precision: The number of decimal places
        
    Returns:
        The formatted percentage string
    """
    return f"{value * 100:.{precision}f}%"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    Format a datetime object.
    
    Args:
        dt: The datetime to format
        format_str: The format string
        
    Returns:
        The formatted datetime string
    """
    return dt.strftime(format_str)


def prepare_chart_data(data: Dict[str, Any]) -> str:
    """
    Prepare data for charts.
    
    Args:
        data: The data to prepare
        
    Returns:
        JSON string of the prepared data
    """
    return json.dumps(data)


def calculate_growth_rate(current: float, previous: float) -> float:
    """
    Calculate growth rate between two values.
    
    Args:
        current: The current value
        previous: The previous value
        
    Returns:
        The growth rate as a decimal
    """
    if previous == 0:
        return 0
    
    return (current - previous) / previous 