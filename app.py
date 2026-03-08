import datetime
from services import (
    add_item, list_items, get_item, record_consumption, forecast_consumption,
    record_attendance, get_attendance_average, plan_next_week, get_dashboard_summary,
    update_item, remove_item
)
from suppliers import get_supplier_suggestions
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# expose a Jinja2 filter that wraps the categorization logic
from suppliers import categorize_item

@app.template_filter('categorize')
def categorize_filter(item_name, extra_labels=''):
    """Template filter to categorize an item name.

    ``extra_labels`` may be a comma-separated string of additional labels
    the AI classifier should consider. This allows templates to supply
    more options than the default set.
    """
    labels = None
    if extra_labels:
        labels = [lbl.strip() for lbl in extra_labels.split(',') if lbl.strip()]
    return categorize_item(item_name, extra_labels=labels)

@app.route('/')
def index():
    summary = get_dashboard_summary()
    return render_template('index.html', **summary)

@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        qty  = int(request.form['quantity'])
        exp  = request.form.get('expires') or None
        cat  = request.form.get('category') or None
        add_item(name, qty, exp, category=cat)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/consume', methods=['GET','POST'])
def consume():
    if request.method == 'POST':
        name = request.form['name']
        qty  = int(request.form['quantity'])
        date = request.form.get('date') or None
        record_consumption(name, qty, date)
        return redirect(url_for('index'))
    items = list_items()
    return render_template('consume.html', items=items)

@app.route('/forecast/<name>')
def forecast(name):
    try:
        item = get_item(name)
        if not item:
            return render_template('forecast.html', name=name, prediction=None, item=None)
        
        prediction = forecast_consumption(name)
        suggestions = get_supplier_suggestions(name, item.quantity, prediction)
        
        return render_template('forecast.html', 
                             name=name, 
                             prediction=prediction,
                             item=item,
                             suggestions=suggestions)
    except KeyError:
        return render_template('forecast.html', name=name, prediction=None, item=None)
    except ValueError as ve:
        # no consumption history case
        return render_template('forecast.html', 
                             name=name, prediction=None, item=item,
                             error=str(ve), suggestions=None)

@app.route('/attendance', methods=['GET','POST'])
def attendance():
    if request.method == 'POST':
        count = int(request.form['count'])
        date = request.form.get('date') or None
        record_attendance(count, date)
        return redirect(url_for('index'))
    return render_template('attendance.html')

@app.route('/plan')
def plan():
    """Display next week's attendance forecast and ordering recommendations."""
    try:
        next_week_forecast = plan_next_week()
        recent_avg = get_attendance_average(7)
        items = list_items()
        today = datetime.date.today()
        
        # supply today_date so template can compare expiration values
        return render_template('plan.html', 
                             next_week_forecast=next_week_forecast,
                             recent_average=recent_avg,
                             items=items,
                             today_date=today)
    except Exception as e:
        return render_template('plan.html', 
                             next_week_forecast=None,
                             recent_average=None,
                             items=[],
                             error=str(e),
                             today_date=datetime.date.today())

@app.route('/edit/<name>', methods=['GET','POST'])
def edit(name):
    """Edit an existing inventory item."""
    item = get_item(name)
    if not item:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        qty = int(request.form['quantity'])
        exp = request.form.get('expires') or None
        cat = request.form.get('category') or None
        try:
            update_item(name, qty, exp, category=cat)
        except KeyError:
            pass
        return redirect(url_for('index'))
    
    return render_template('edit.html', item=item)

@app.route('/delete/<name>', methods=['POST'])
def delete(name):
    """Delete an inventory item."""
    try:
        remove_item(name)
    except Exception:
        pass
    return redirect(url_for('index'))