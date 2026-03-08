"""Service layer for Inventory and Attendance operations.

Exposes a shared inventory and attendance tracker instance, plus
helper functions for use by the CLI and web app.
"""

import datetime
from main import Inventory, InventoryItem, AttendanceTracker

# Global shared instances
inventory = Inventory()
attendance_tracker = AttendanceTracker()


# --- Item management ---

def add_item(name, quantity, expiration_date=None, category=None):
    """Add or update an item in inventory.
    
    Args:
        name (str): item name
        quantity (int): quantity to add
        expiration_date (datetime.date or str): optional expiration date
        category (str|None): optional manual category override
        
    Returns:
        InventoryItem: the updated item
    """
    if isinstance(expiration_date, str):
        expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d").date()
    
    item = inventory.get_item(name)
    if not item:
        item = InventoryItem(name, quantity, expiration_date, category=category)
    else:
        item.quantity += quantity
        if expiration_date:
            item.expiration_date = expiration_date
        if category:
            item.category = category
    
    inventory.add_item(item)
    return item


def update_item(name, quantity, expiration_date=None, category=None):
    """Update an existing item's quantity, expiration date, and optional category.
    
    Args:
        name (str): item name
        quantity (int): new quantity (replaces current)
        expiration_date (datetime.date or str): optional new expiration date
        category (str|None): optional new category override
        
    Returns:
        InventoryItem: the updated item
        
    Raises:
        KeyError: if item not found
    """
    if isinstance(expiration_date, str):
        expiration_date = datetime.datetime.strptime(expiration_date, "%Y-%m-%d").date()
    
    item = inventory.get_item(name)
    if not item:
        raise KeyError(f"No such item: {name}")
    
    item.quantity = quantity
    if expiration_date:
        item.expiration_date = expiration_date
    if category is not None:
        item.category = category
    
    inventory.add_item(item)
    return item


def list_items(name_filter=None, expire_before=None):
    """List items with optional filters.
    
    Args:
        name_filter (str): optional substring to filter by name
        expire_before (datetime.date or str): optional expiration cutoff
        
    Returns:
        list: filtered items
    """
    if isinstance(expire_before, str):
        expire_before = datetime.datetime.strptime(expire_before, "%Y-%m-%d").date()
    
    return inventory.list_items(name_filter=name_filter, expire_before=expire_before)


def get_item(name):
    """Retrieve a single item by name.
    
    Returns:
        InventoryItem or None
    """
    return inventory.get_item(name)


def remove_item(name):
    """Remove an item from inventory."""
    inventory.remove_item(name)


def record_consumption(name, amount, date=None):
    """Log consumption for an item.
    
    Args:
        name (str): item name
        amount (int): quantity consumed
        date (datetime.date or str): optional date (defaults to today)
        
    Raises:
        KeyError: if item not found
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    
    inventory.record_consumption(name, amount, date)


def forecast_consumption(name, days=7):
    """Forecast future consumption using AI with fallback.
    
    Args:
        name (str): item name
        days (int): days to forecast (default 7)
        
    Returns:
        float: predicted quantity
        
    Raises:
        KeyError: if item not found
    """
    return inventory.forecast_consumption(name, days)


# --- Attendance management ---

def record_attendance(count, date=None):
    """Log customer attendance.
    
    Args:
        count (int): number of attendees
        date (datetime.date or str): optional date (defaults to today)
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    
    attendance_tracker.record(count, date)


def get_attendance_average(days=7):
    """Get average attendance over N days.
    
    Args:
        days (int): lookback period
        
    Returns:
        float: average daily attendance
    """
    return attendance_tracker.average(days)


def plan_next_week():
    """Forecast attendance for next week using AI with fallback.
    
    Returns:
        float: expected attendance count
    """
    return attendance_tracker.plan_next_week()


# --- Convenience summary functions ---

def get_dashboard_summary():
    """Return all data needed for the dashboard.
    
    Returns:
        dict with keys: items, total_quantity, recent_attendance, forecast
    """
    items = list_items()
    # annotate each item with a category for display (unless user has set one)
    try:
        from suppliers import categorize_item
        for item in items:
            if not getattr(item, 'category', None):
                item.category = categorize_item(item.name)
    except ImportError:
        # if suppliers module missing, just default to 'unknown'
        for item in items:
            if not getattr(item, 'category', None):
                item.category = 'unknown'

    total_qty = sum(item.quantity for item in items)
    recent_attendance = get_attendance_average(7)
    forecast = plan_next_week() if attendance_tracker.records else 0
    
    return {
        'items': items,
        'total_quantity': total_qty,
        'recent_attendance': round(recent_attendance, 2),
        'next_week_forecast': round(forecast, 2),
    }


def get_expiring_soon(days=3):
    """Get items expiring within N days.
    
    Args:
        days (int): cutoff (default 3)
        
    Returns:
        list: items expiring soon
    """
    cutoff = datetime.date.today() + datetime.timedelta(days=days)
    return inventory.list_items(expire_before=cutoff)