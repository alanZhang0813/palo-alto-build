# Green-Tech Inventory Assistant – Design Document

## Overview

## 1. Project Goals

1. **Waste Reduction**: Enable users to forecast consumption accurately and plan ordering based on expected demand.
2. **Ease of Entry**: Provide a simple, intuitive interface for adding items, recording consumption, and managing inventory.
3. **AI Application with Fallback**: Integrate multiple AI capabilities with robust fallbacks for when services are unavailable.
4. **Core End-to-End Flow**: Support complete inventory lifecycle—create, read, update, delete—plus forecasting and planning.
5. **Sustainable Sourcing**: Recommend suppliers prioritizing eco-friendly and local practices.

---

## 2. Tech Stack

### Backend

- **Python 3.11.9**: Core language for logic and data handling.
- **Flask**: Lightweight web framework for routing and templating (Jinja2).
- **datetime & statistics**: Standard library modules for date handling and averages.
- **scikit-learn**: Linear regression for consumption/attendance forecasting.
- **transformers (Hugging Face)**: Zero-shot classification for item categorization.

### Frontend

- **Bootstrap 5.1.3**: Responsive CSS framework for styling and layout.
- **Jinja2**: Template engine for dynamic HTML rendering.
- **HTML5**: Semantic markup for forms and UI components.

### Development & Testing

- **unittest**: Built-in Python testing framework for unit and integration tests.
- **Git**: Version control for tracking changes and collaboration.

### Deployment Ready

- No database currently (items stored in-memory); can be extended with SQLite, PostgreSQL, etc.
- Flask development server suitable for prototyping; production deployment via WSGI (Gunicorn, uWSGI).

---

## 3. Architecture

### Directory Structure

```
palo-alto-build/
├── main.py                 # Core classes: Inventory, InventoryItem, AttendanceTracker
├── services.py             # Service layer: shared functions for CLI/web
├── suppliers.py            # Supplier database & categorization logic (AI)
├── app.py                  # Flask routes and web app
├── tests/
│   └── test_main.py        # 15+ unit tests covering all major features
├── templates/              # Jinja2 templates for web UI
│   ├── index.html          # Dashboard & inventory list
│   ├── add.html            # Add item form
│   ├── edit.html           # Edit item form
│   ├── consume.html        # Record consumption form
│   ├── forecast.html       # Consumption forecast & supplier suggestions
│   ├── attendance.html     # Record attendance form
│   ├── plan.html           # Weekly planning & ordering guidance
│   └── ...
├── .venv/                  # Virtual environment (excluded from git)
├── .gitignore
├── README.md
└── design_doc.md           # This file
```

### Core Components

#### 1. **Inventory Management (main.py)**

- **InventoryItem**: Represents a single item with name, quantity, expiration date, optional category, and consumption history.
  - Methods: `record_consumption()`, `average_consumption(days)`, `__str__()`
- **Inventory**: Collection of items with CRUD operations and filtering.
  - Methods: `add_item()`, `remove_item()`, `get_item()`, `list_items()`, `record_consumption()`, `forecast_consumption()`
- **AttendanceTracker**: Tracks daily customer attendance for demand planning.
  - Methods: `record()`, `average(days)`, `plan_next_week()` (with AI prediction)

#### 2. **Services Layer (services.py)**

- Exposes shared functions for both CLI and web app.
- Global instances: `inventory`, `attendance_tracker`.
- High-level operations: `add_item()`, `update_item()`, `list_items()`, `forecast_consumption()`, `record_attendance()`, `plan_next_week()`, `get_dashboard_summary()`.
- Acts as abstraction layer between Flask routes and core logic.

#### 3. **Supplier Management (suppliers.py)**

- **SUSTAINABLE_SUPPLIERS**: Curated dictionary of suppliers categorized by product type (produce, beverages, dairy, grains, protein, default).
  - Each supplier entry includes name, distance, benefits, and sustainability notes.
- **categorize_item(item_name, extra_labels=None)**: AI-powered categorization using zero-shot classification (Hugging Face) with keyword fallback.
  - Accepts optional extra category labels for custom use cases.
  - Falls back gracefully if AI model fails.
- **get_supplier_suggestions(item_name, on_hand, predicted_consumption)**: Returns supplier recommendations and shortage warnings.

#### 4. **Flask Web App (app.py)**

- Routes:
  - `GET /`: Dashboard showing summary and inventory list.
  - `GET/POST /add`: Add new item form and submission.
  - `GET/POST /consume`: Record consumption form and submission.
  - `GET /forecast/<name>`: Detailed forecast with supplier suggestions.
  - `GET/POST /attendance`: Record attendance form and submission.
  - `GET /plan`: Weekly planning page with forecasts and recommendations.
  - `GET/POST /edit/<name>`: Edit item details (quantity, expiration, category).
  - `POST /delete/<name>`: Delete inventory item.
- Jinja2 custom filter: `{{ item_name | categorize('extra,labels') }}`

#### 5. **Web UI (templates/)**

- Responsive Bootstrap 5 design.
- Forms for all CRUD operations with input validation.
- Dashboard cards showing total inventory, recent attendance, and forecast.
- Detailed forecast page showing supplier options for sustainable sourcing.
- Weekly planning guide with alerts for increased/decreased demand.

---

## 4. AI Integrations

### 4.1 Consumption Forecasting

- **Model**: Linear regression (scikit-learn).
- **Data**: Historical consumption records (date, amount).
- **Use Case**: Predict 7-day consumption to determine if current stock is sufficient.
- **Fallback**: Simple average of past consumption × forecast days.
- **Reliability**: Simulated 10% random failure rate to test fallback behavior; real deployments would handle network/service errors.

### 4.2 Attendance Prediction

- **Model**: Linear regression on historical attendance records.
- **Data**: Daily attendance counts.
- **Use Case**: Forecast next week's attendance to help plan consumption levels.
- **Fallback**: 7-day rolling average × 7 days.
- **Output**: Guides ordering and inventory planning.

### 4.3 Item Categorization

- **Model**: Zero-shot classification (Hugging Face `typeform/distilbert-base-uncased-mnli`).
- **Data**: Item name (text input).
- **Candidates**: produce, beverages, dairy, grains, protein (+ optional extras).
- **Use Case**: Automatically classify items to suggest relevant sustainable suppliers.
- **Fallback**: Keyword matching on known product terms (e.g., "apple" → produce, "coffee" → beverages).
- **Manual Override**: Users can explicitly set a category when adding/editing items.

---

## 5. Key Features

### Inventory Management

- Add items with name, quantity, expiration date, and optional category.
- Edit quantity, expiration, and category for any item.
- Delete items from inventory.
- Record consumption entries (date-stamped).
- Filter items by name or expiration date.

### Forecasting & Planning

- 7-day consumption forecast using AI with fallback.
- Shortage alerts when stock may run out.
- 7-day attendance forecast for demand planning.
- Weekly planning page with visual guidance (increased/stable/decreased demand).

### Sustainable Sourcing

- Supplier recommendations for each product category.
- Emphasis on local, organic, fair-trade, and low-impact suppliers.
- Suggestions triggered automatically when inventory may run short.

### Consumption History Tracking

- All consumption records stored with timestamps.
- Used for trend analysis and forecasting.
- Clear error message if forecasting is attempted without any consumption history.

### Attendance Planning

- Record attendance for any date.
- Rolling average calculation.
- AI-based forecasting for next week.
- Inform ordering decisions based on expected demand.

---

## 6. Testing

### Test Coverage (15 tests)

- **Inventory Operations**: add, retrieve, list, filter, record consumption, forecast with fallback.
- **Attendance Operations**: record, average, plan next week.
- **AI Fallbacks**: Verify that AI predictions fail gracefully and trigger fallback behavior.
- **Dashboard Summary**: Ensure categories are annotated and include AI categorization.
- **Forecast Error Handling**: Verify helpful error messages when no consumption history exists.
- **Manual Category Editing**: Confirm that user-set categories persist and are respected.
- **Template Filter**: Validate that the `categorize` Jinja filter is registered and callable.

### Execution

```bash
python -m unittest tests.test_main -v
```

All tests pass successfully.

---

## 7. Data Flow

### Adding an Item

1. User visits `/add` form.
2. Submits name, quantity, expiration date, and optional category.
3. Flask route calls `services.add_item()`.
4. Service creates/updates `InventoryItem` and stores in global `inventory`.
5. Dashboard refreshes to show new item (with AI-categorized or manual category).

### Recording Consumption

1. User visits `/consume` form.
2. Selects item and quantity consumed.
3. Flask route calls `services.record_consumption()`.
4. Service calls `item.record_consumption()` to append to history.
5. History now available for consumption forecasting.

### Forecasting

1. User clicks forecast button or visits `/forecast/<item_name>`.
2. Flask route checks for consumption history; raises `ValueError` if none.
3. If history exists, calls `services.forecast_consumption()`.
4. Service invokes `inventory.forecast_consumption()`:
   - Attempts AI prediction (linear regression).
   - Falls back to average if AI fails.
5. Template displays forecast, compares with current stock, suggests suppliers if shortage risk.

### Planning Next Week

1. User visits `/plan` page.
2. Flask provides `plan_next_week()` forecast and `today_date` context.
3. Dashboard shows:
   - Recent attendance (7-day avg).
   - Next week's forecast.
   - Alerts (increased/stable/decreased demand).
   - Current inventory with status badges.
4. User can refine orders based on guidance.

---

## 8. Future Enhancements

### Short-term (High Priority)

1. **Persistent Storage**
   - Replace in-memory inventory with SQLite or PostgreSQL.
   - Store consumption history permanently.
   - Track attendance records over time.

2. **Advanced Filtering & Search**
   - Filter inventory by category, expiration range, stock level.
   - Search items by name or category.
   - Export inventory as CSV.

3. **Batch Operations**
   - Record consumption for multiple items at once.
   - Bulk edit categories or expirations.
   - Batch add items from template.

4. **Improved Forecasting**
   - Seasonal trend detection (e.g., higher attendance in summer).
   - Exponential smoothing for smoother predictions.
   - Item-specific forecasting models (some items stable, others volatile).

### Medium-term (Nice to Have)

5. **User Accounts & Authentication**
   - Multi-user support with login.
   - Role-based access (admin, staff, viewer).
   - Audit log for inventory changes.

6. **Notifications & Alerts**
   - Email/SMS alerts when stock runs low.
   - Expiration reminders.
   - Weekly summary reports.

7. **Enhanced Supplier Integration**
   - API integration with supplier platforms (e.g., direct ordering).
   - Price comparisons across suppliers.
   - Shipping cost estimation.

8. **Mobile App**
   - React Native or Flutter mobile companion.
   - Quick capture of consumption via QR codes.
   - Offline-first architecture with sync.

### Long-term (Aspirational)

9. **Machine Learning Enhancements**
   - Deep learning models for demand prediction (LSTM, Transformer).
   - Anomaly detection for unusual consumption patterns.
   - Automatically suggest optimal reorder points per item.

10. **Sustainability Scoring**
    - Track carbon footprint of orders.
    - Calculate waste reduction over time.
    - Gamify sustainable choices (badges, leaderboards).

11. **Supply Chain Optimization**
    - Route optimization for multi-supplier orders.
    - Collaborative purchasing with other organizations.
    - Dynamic pricing based on demand and inventory.

12. **Integration with Third-party Services**
    - Connect to accounting software (QuickBooks, Xero).
    - Analytics dashboards (Google Data Studio, Tableau).
    - Inventory syncing with e-commerce platforms.

---

## 9. Deployment & Operations

### Development

```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install Flask transformers torch scikit-learn

# Run tests
python -m unittest tests.test_main -v

# Start Flask dev server
flask run  # runs on http://localhost:5000
```

### Production

- Use WSGI server: `gunicorn app:app`.
- Add PostgreSQL for data persistence.
- Enable HTTPS/SSL.
- Set up logging and monitoring.
- Deploy via Docker, AWS, Heroku, or similar.

### Scaling

- Separate AI/forecasting into async tasks (Celery, APScheduler).
- Cache model weights locally to reduce download time.
- Use CDN for static assets (Bootstrap, JS).

---

## 10. Security Considerations

- **Input Validation**: Sanitize user input in forms (dates, quantities, strings).
- **CSRF Protection**: Add Flask-WTF for form token validation.
- **Database**: Use parameterized queries to prevent SQL injection.
- **API Security**: If exposing APIs, implement rate limiting and API keys.
- **Model Safety**: Validate AI model outputs; don't blindly trust predictions.

---

## 11. Dependencies

### Core

- `Flask` – Web framework
- `scikit-learn` – Machine learning (regression)
- `transformers` – NLP/zero-shot classification
- `torch` – Deep learning backend for transformers

### Optional (for future features)

- `SQLAlchemy` – ORM for database management
- `Celery` – Async task queue
- `APScheduler` – Job scheduling
- `python-dotenv` – Environment variable management
- `requests` – HTTP client for external APIs
- `pytest` – Alternative testing framework

---

## 12. Lessons Learned & Best Practices

1. **Fallback-First Design**: Always provide a manual/rule-based fallback for AI features to ensure reliability.
2. **Service Layer**: Separating business logic from routes makes code reusable and testable.
3. **Clear Error Messages**: Help users understand why operations fail (e.g., "No consumption history recorded").
4. **Incremental Development**: Build core features first (inventory CRUD), then add AI, then optimize.
5. **Test Coverage**: Unit tests validate both success and failure paths (e.g., AI failure scenarios).
6. **Sustainable Design**: Choose suppliers and recommendations that align with environmental goals.

---

## 13. Conclusion

The Green-Tech Inventory Assistant demonstrates how AI can enhance practical business operations without compromising reliability. By layering intelligent forecasting on top of robust manual fallbacks, the system provides value even when AI services are unavailable. The modular design—clean separation of concerns via services, routes, and models—makes the codebase maintainable and extensible for future enhancements.

Next steps: persist data to a database, add user authentication, and expand forecasting models to handle seasonal trends.

---

**Document Version**: 1.0  
**Last Updated**: March 8, 2026  
**Author**: AI Assistant (GitHub Copilot)
