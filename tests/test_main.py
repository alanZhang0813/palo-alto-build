import datetime
import unittest

from main import Inventory, InventoryItem, AttendanceTracker, ai_predict_consumption, ai_predict_attendance


class TestInventory(unittest.TestCase):
    def setUp(self):
        self.inv = Inventory()
        self.item = InventoryItem("apple", 10, expiration_date=datetime.date.today())
        self.inv.add_item(self.item)

    def test_add_and_get(self):
        got = self.inv.get_item("apple")
        self.assertIs(got, self.item)

    def test_list_filter(self):
        results = self.inv.list_items(name_filter="app")
        self.assertIn(self.item, results)
        results = self.inv.list_items(expire_before=datetime.date.today())
        self.assertIn(self.item, results)

    def test_record_consumption_and_quantity(self):
        self.inv.record_consumption("apple", 3)
        self.assertEqual(self.item.quantity, 7)
        self.assertEqual(self.item.consumption_history[-1][1], 3)

    def test_forecast_fallback(self):
        # when there is no history the method should raise a ValueError
        with self.assertRaises(ValueError):
            self.inv.forecast_consumption("apple", days=5)

        # add some history and try again
        self.item.record_consumption(2, date=datetime.date.today() - datetime.timedelta(days=1))
        qty2 = self.inv.forecast_consumption("apple", days=2)
        self.assertGreaterEqual(qty2, 0)

    def test_forecast_route_no_history_message(self):
        # ensure the forecast page shows a helpful error when no history exists
        from app import app as flask_app
        from services import add_item
        # add item without any consumption history
        add_item("apple", 10)
        client = flask_app.test_client()
        response = client.get('/forecast/apple')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cannot Forecast", response.data)
        self.assertIn(b"Record Consumption", response.data)

    def test_missing_item_raises(self):
        with self.assertRaises(KeyError):
            self.inv.record_consumption("banana", 1)


class TestAttendance(unittest.TestCase):
    def setUp(self):
        self.tracker = AttendanceTracker()

    def test_record_and_average(self):
        self.tracker.record(5, date=datetime.date.today())
        avg = self.tracker.average(days=1)
        self.assertEqual(avg, 5)

    def test_plan_next_week(self):
        self.tracker.record(3)
        expected = self.tracker.plan_next_week()
        self.assertIsInstance(expected, float)


class TestDashboard(unittest.TestCase):
    def test_summary_includes_category(self):
        # ensure get_dashboard_summary annotates items with category
        from services import get_dashboard_summary, add_item, update_item
        # add with manual category
        add_item("banana", 5, category="fruit")
        summary = get_dashboard_summary()
        items = summary['items']
        self.assertTrue(items)
        # locate banana in the returned list
        banana_item = next(i for i in items if i.name == "banana")
        self.assertEqual(banana_item.category, "fruit")
        # update without category should leave it unchanged
        update_item("banana", 10)
        summary2 = get_dashboard_summary()
        banana_item2 = next(i for i in summary2['items'] if i.name == "banana")
        self.assertEqual(banana_item2.category, "fruit")

    def test_manual_category_editing(self):
        from services import add_item, update_item, get_dashboard_summary
        # add item without category
        add_item("cereal", 4)
        # dashboard should auto categorize
        initial = get_dashboard_summary()['items'][0].category
        self.assertIn(initial, ["produce","beverages","dairy","grains","protein","default"])
        # now update with explicit overriding category
        update_item("cereal", 4, category="breakfast")
        updated = get_dashboard_summary()['items'][0].category
        self.assertEqual(updated, "breakfast")

    def test_plan_view_uses_today_date(self):
        # Add an item expiring today and confirm /plan renders the 'Today' badge
        from services import add_item
        from app import app as flask_app
        import datetime

        today = datetime.date.today()
        # create an item expiring today
        add_item("yogurt", 3, expiration_date=today)

        client = flask_app.test_client()
        response = client.get('/plan')
        self.assertEqual(response.status_code, 200)
        # the template should include the 'Today' badge text when comparing with today_date
        self.assertIn(b"Today", response.data)

    def test_categorize_with_extra_labels(self):
        # direct call should honor extra_labels parameter
        from suppliers import categorize_item
        result = categorize_item("industrial glue", extra_labels=["industrial", "cleaning"])
        # result should be one of our labels (may default or match extra)
        self.assertIn(result, ["produce", "beverages", "dairy", "grains", "protein", "industrial", "cleaning", "default"])

    def test_template_filter_extra(self):
        # ensure the categorize filter is registered and accepts extras
        from app import app as flask_app
        with flask_app.app_context():
            filt = flask_app.jinja_env.filters.get('categorize')
            self.assertIsNotNone(filt)
            out = filt("lab solvent", "lab,chemical")
            self.assertIsInstance(out, str)

class TestAIFallback(unittest.TestCase):
    def test_ai_predict_consumption_failure(self):
        # simulate by running until exception occurs
        history = [(datetime.date.today(), 1)]
        fail = False
        for _ in range(50):  # Increased iterations for lower failure rate
            try:
                ai_predict_consumption(history, 3)
            except RuntimeError:
                fail = True
                break
        self.assertTrue(fail, "ai_predict_consumption should sometimes raise")

    def test_ai_predict_attendance_failure(self):
        recs = {datetime.date.today(): 10}
        fail = False
        for _ in range(50):  # Increased iterations for lower failure rate
            try:
                ai_predict_attendance(recs)
            except RuntimeError:
                fail = True
                break
        self.assertTrue(fail)


if __name__ == "__main__":
    unittest.main()
