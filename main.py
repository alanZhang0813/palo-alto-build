import datetime
from statistics import mean
import argparse

class InventoryItem:
    """Represents a single inventory item including consumption history.

    Attributes:
        name (str): unique item name
        quantity (int): current on-hand quantity
        expiration_date (datetime.date|None): optional expiration date
        consumption_history (list): list of (date, amount) tuples
    """

    def __init__(self, name, quantity, expiration_date=None, category=None):
        self.name = name
        self.quantity = quantity
        self.expiration_date = expiration_date
        # optional manual category override
        self.category = category
        self.consumption_history = []  # [(date, amount), ...]

    def __str__(self):
        exp = f" - Expires: {self.expiration_date}" if self.expiration_date else ""
        return f"{self.name} (x{self.quantity}){exp}"

    def record_consumption(self, amount, date=None):
        """Log consumption and decrease quantity."""
        if date is None:
            date = datetime.date.today()
        self.consumption_history.append((date, amount))
        self.quantity = max(0, self.quantity - amount)

    def average_consumption(self, days=30):
        """Compute average daily consumption over the past *days*.

        Falls back to 0 if no history is available.
        """
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        amounts = [amt for (dt, amt) in self.consumption_history if dt >= cutoff]
        if not amounts:
            return 0
        # total consumed divided by actual days recorded
        return sum(amounts) / days


class Inventory:
    """Collection of InventoryItem objects with utility methods."""

    def __init__(self):
        # use dict for quick lookup by name
        self.items = {}

    def add_item(self, item):
        self.items[item.name] = item

    def remove_item(self, name):
        self.items.pop(name, None)

    def get_item(self, name):
        return self.items.get(name)

    def list_items(self, name_filter=None, expire_before=None):
        """Return list of items optionally filtered by name substring or expiration."""
        result = list(self.items.values())
        if name_filter:
            result = [i for i in result if name_filter.lower() in i.name.lower()]
        if expire_before:
            result = [i for i in result if i.expiration_date and i.expiration_date <= expire_before]
        return result

    def record_consumption(self, name, amount, date=None):
        item = self.get_item(name)
        if not item:
            raise KeyError(f"No such item: {name}")
        item.record_consumption(amount, date)

    def forecast_consumption(self, name, days=7):
        """Try to use AI to predict consumption; fall back to simple average."""
        item = self.get_item(name)
        if not item:
            raise KeyError(f"No such item: {name}")
        # If there is no recorded consumption history at all, signal this clearly
        if not item.consumption_history:
            raise ValueError("No consumption history recorded for this item")
        try:
            return ai_predict_consumption(item.consumption_history, days)
        except Exception:
            # manual rule: average consumption * days
            return item.average_consumption(days) * days


class AttendanceTracker:
    """Tracks customer attendance for planning purposes."""

    def __init__(self):
        self.records = {}  # date -> count

    def record(self, count, date=None):
        if date is None:
            date = datetime.date.today()
        self.records[date] = self.records.get(date, 0) + count

    def average(self, days=7):
        cutoff = datetime.date.today() - datetime.timedelta(days=days)
        vals = [c for d, c in self.records.items() if d >= cutoff]
        if not vals:
            return 0
        return sum(vals) / days

    def plan_next_week(self):
        """Return expected attendance for the next week, with AI fallback."""
        try:
            return ai_predict_attendance(self.records)
        except Exception:
            return self.average(7) * 7


# --- AI integration stubs --------------------------------------------------

def _linear_regression_predict(x_values, y_values, future_x):
    """Simple linear regression implementation using standard library."""
    if len(x_values) < 2:
        # Not enough data for regression, return average
        return sum(y_values) / len(y_values) if y_values else 0
    
    n = len(x_values)
    sum_x = sum(x_values)
    sum_y = sum(y_values)
    sum_xy = sum(x * y for x, y in zip(x_values, y_values))
    sum_x2 = sum(x * x for x in x_values)
    
    # Calculate slope and intercept
    denominator = n * sum_x2 - sum_x * sum_x
    if denominator == 0:
        return sum(y_values) / len(y_values)
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    return slope * future_x + intercept


def ai_predict_consumption(history, days):
    """AI-based consumption forecast using linear regression on historical data.
    
    Analyzes consumption trends and predicts future consumption.
    Falls back to average if insufficient data.
    """
    import random
    
    # Simulate occasional service unavailability (reduced from 50% to 10%)
    if random.random() < 0.1:
        raise RuntimeError("AI service unavailable - network timeout")
    
    if not history or len(history) < 2:
        # Not enough data, use simple average
        total = sum(amt for (_, amt) in history) if history else 0
        avg_daily = total / 30 if history else 0  # Assume 30 days of history
        return avg_daily * days
    
    # Prepare data for regression: days since first record vs consumption
    base_date = min(dt for dt, _ in history)
    x_values = []  # days since start
    y_values = []  # consumption amounts
    
    for dt, amt in history:
        days_since_start = (dt - base_date).days
        x_values.append(days_since_start)
        y_values.append(amt)
    
    # Predict consumption for each future day and sum
    total_predicted = 0
    for day_offset in range(1, days + 1):
        future_x = (datetime.date.today() - base_date).days + day_offset
        predicted_daily = _linear_regression_predict(x_values, y_values, future_x)
        total_predicted += max(0, predicted_daily)  # Ensure non-negative
    
    return total_predicted


def ai_predict_attendance(records):
    """AI-based attendance forecast using trend analysis.
    
    Analyzes attendance patterns and predicts next week's total attendance.
    """
    import random
    
    # Simulate occasional service unavailability
    if random.random() < 0.1:
        raise RuntimeError("AI service unavailable - model loading failed")
    
    if not records or len(records) < 3:
        # Not enough data, use simple average
        total = sum(records.values()) if records else 0
        avg_daily = total / len(records) if records else 0
        return avg_daily * 7
    
    # Prepare data for regression: days since earliest record vs attendance
    base_date = min(records.keys())
    x_values = []  # days since start
    y_values = []  # attendance counts
    
    for dt, count in sorted(records.items()):
        days_since_start = (dt - base_date).days
        x_values.append(days_since_start)
        y_values.append(count)
    
    # Predict attendance for next 7 days
    total_predicted = 0
    for day_offset in range(1, 8):  # Next 7 days
        future_x = (datetime.date.today() - base_date).days + day_offset
        predicted_daily = _linear_regression_predict(x_values, y_values, future_x)
        total_predicted += max(0, predicted_daily)  # Ensure non-negative
    
    return total_predicted


# --- basic command‑line interface for demonstration -----------------------

def main():
    parser = argparse.ArgumentParser(description="Green-Tech Inventory Assistant CLI")
    sub = parser.add_subparsers(dest="cmd")

    add = sub.add_parser("add", help="Add or update an item")
    add.add_argument("name")
    add.add_argument("quantity", type=int)
    add.add_argument("--expires", type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date(),
                     help="expiration date YYYY-MM-DD")

    listp = sub.add_parser("list", help="List items")
    listp.add_argument("--filter")
    listp.add_argument("--expire-before", type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d").date())

    cons = sub.add_parser("consume", help="Record consumption")
    cons.add_argument("name")
    cons.add_argument("amount", type=int)

    forecast = sub.add_parser("forecast", help="Forecast future consumption")
    forecast.add_argument("name")
    forecast.add_argument("--days", type=int, default=7)

    attend = sub.add_parser("attendance", help="Record attendance")
    attend.add_argument("count", type=int)

    plan = sub.add_parser("plan", help="Plan attendance for next week")

    args = parser.parse_args()
    from services import (
        add_item, list_items, record_consumption, forecast_consumption,
        record_attendance, plan_next_week
    )

    if args.cmd == "add":
        item = add_item(args.name, args.quantity, args.expires)
        print(f"Added: {item}")
    elif args.cmd == "list":
        items = list_items(name_filter=args.filter, expire_before=args.expire_before)
        for it in items:
            print(it)
    elif args.cmd == "consume":
        record_consumption(args.name, args.amount)
        print(f"Recorded consumption of {args.amount} from {args.name}")
    elif args.cmd == "forecast":
        qty = forecast_consumption(args.name, args.days)
        print(f"Predicted consumption for {args.name} over {args.days} days: {qty:.1f}")
    elif args.cmd == "attendance":
        record_attendance(args.count)
        print(f"Recorded attendance {args.count}")
    elif args.cmd == "plan":
        expected = plan_next_week()
        print(f"Expected attendance next week: {expected:.1f}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()