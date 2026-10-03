import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'laboratory_stock_secret_key_98765')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/laboratory_stock')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'laboratory_stock.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CATEGORIES = [
    'Computer Equipment',
    'Electronic Components',
    'Laboratory Equipment',
    'Stationery',
    'Other'
]

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    item_code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock = db.Column(db.Integer, nullable=False, default=5)
    unit = db.Column(db.String(20), nullable=False, default='Pcs')
    location = db.Column(db.String(100), nullable=False, default='Main Lab')
    added_date = db.Column(db.Date, nullable=False, default=date.today)

    stock_logs = db.relationship('StockHistory', backref='item', lazy=True, cascade='all, delete-orphan')

    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'Out of Stock'
        elif self.quantity <= self.minimum_stock:
            return 'Low Stock'
        else:
            return 'In Stock'

    @property
    def stock_badge_class(self):
        if self.stock_status == 'In Stock':
            return 'bg-success'
        elif self.stock_status == 'Low Stock':
            return 'bg-warning text-dark'
        else:
            return 'bg-danger'


class StockHistory(db.Model):
    __tablename__ = 'stock_history'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'Stock Added', 'Stock Used'
    date = db.Column(db.DateTime, default=datetime.utcnow)
    remarks = db.Column(db.String(255), nullable=True)


# Auth Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Admin authentication required. Please log in.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def seed_default_data():
    if db.session.query(Admin).count() == 0:
        default_admin = Admin(username='admin')
        default_admin.set_password('admin123')
        db.session.add(default_admin)
        db.session.commit()

    if db.session.query(Item).count() == 0:
        sample_items = [
            Item(item_name='Desktop PC i5 12th Gen', item_code='COMP-001', category='Computer Equipment', quantity=25, minimum_stock=5, unit='Units', location='Lab 1 - Rack A', added_date=date.today()),
            Item(item_name='Optical Mouse USB', item_code='COMP-002', category='Computer Equipment', quantity=40, minimum_stock=10, unit='Pcs', location='Lab 1 - Shelf B', added_date=date.today()),
            Item(item_name='Arduino Uno R3', item_code='ELEC-001', category='Electronic Components', quantity=15, minimum_stock=5, unit='Pcs', location='Electronics Lab - Cabinet 1', added_date=date.today()),
            Item(item_name='Resistor Kit (10k Ohm)', item_code='ELEC-002', category='Electronic Components', quantity=3, minimum_stock=10, unit='Packs', location='Electronics Lab - Drawer 3', added_date=date.today()),
            Item(item_name='Digital Multimeter', item_code='LAB-001', category='Laboratory Equipment', quantity=8, minimum_stock=2, unit='Units', location='Testing Bay 2', added_date=date.today()),
            Item(item_name='Oscilloscope 50MHz', item_code='LAB-002', category='Laboratory Equipment', quantity=0, minimum_stock=2, unit='Units', location='Testing Bay 1', added_date=date.today()),
            Item(item_name='A4 Printing Paper', item_code='STAT-001', category='Stationery', quantity=50, minimum_stock=10, unit='Reams', location='Store Room - Shelf A', added_date=date.today()),
            Item(item_name='Whiteboard Markers', item_code='STAT-002', category='Stationery', quantity=2, minimum_stock=5, unit='Boxes', location='Store Room - Shelf B', added_date=date.today()),
        ]
        db.session.add_all(sample_items)
        db.session.commit()

        # Seed stock history
        for item in sample_items:
            history = StockHistory(
                item_id=item.id,
                quantity=item.quantity,
                transaction_type='Stock Added',
                remarks='Initial stock setup'
            )
            db.session.add(history)
        db.session.commit()


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('user_type') == 'admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and Password are required.', 'danger')
            return redirect(url_for('admin_login'))

        admin = db.session.query(Admin).filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_name'] = admin.username
            flash(f'Welcome back, {admin.username}! Successfully logged in.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    items = db.session.query(Item).all()

    total_items = len(items)
    available_items = len([i for i in items if i.stock_status == 'In Stock'])
    low_stock_items = len([i for i in items if i.stock_status == 'Low Stock'])
    out_of_stock_items = len([i for i in items if i.stock_status == 'Out of Stock'])

    recent_history = db.session.query(StockHistory).order_by(StockHistory.date.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_items=total_items,
        available_items=available_items,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        recent_history=recent_history
    )


@app.route('/admin/items')
@admin_required
def items_list():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = db.session.query(Item)

    if search_query:
        query = query.filter(
            (Item.item_name.ilike(f'%{search_query}%')) |
            (Item.item_code.ilike(f'%{search_query}%'))
        )

    if category_filter:
        query = query.filter(Item.category == category_filter)

    all_items = query.order_by(Item.item_name.asc()).all()

    # Filter stock status in Python since it's a property
    if status_filter:
        all_items = [i for i in all_items if i.stock_status == status_filter]

    return render_template(
        'items.html',
        items=all_items,
        categories=CATEGORIES,
        search_query=search_query,
        category_filter=category_filter,
        status_filter=status_filter
    )


@app.route('/admin/items/add', methods=['GET', 'POST'])
@admin_required
def add_item():
    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        item_code = request.form.get('item_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        quantity = request.form.get('quantity', type=int)
        minimum_stock = request.form.get('minimum_stock', type=int)
        unit = request.form.get('unit', '').strip()
        location = request.form.get('location', '').strip()
        added_date_str = request.form.get('added_date', '')

        if not item_name or not item_code or not category or quantity is None or minimum_stock is None or not unit or not location:
            flash('All fields are required.', 'danger')
            return redirect(url_for('add_item'))

        if quantity < 0:
            flash('Quantity cannot be negative.', 'danger')
            return redirect(url_for('add_item'))

        if minimum_stock < 0:
            flash('Minimum stock threshold cannot be negative.', 'danger')
            return redirect(url_for('add_item'))

        existing_code = db.session.query(Item).filter_by(item_code=item_code).first()
        if existing_code:
            flash(f'An item with Item Code "{item_code}" already exists.', 'danger')
            return redirect(url_for('add_item'))

        try:
            added_date = datetime.strptime(added_date_str, '%Y-%m-%d').date() if added_date_str else date.today()
        except ValueError:
            added_date = date.today()

        new_item = Item(
            item_name=item_name,
            item_code=item_code,
            category=category,
            quantity=quantity,
            minimum_stock=minimum_stock,
            unit=unit,
            location=location,
            added_date=added_date
        )
        db.session.add(new_item)
        db.session.commit()

        # Record initial stock history
        history = StockHistory(
            item_id=new_item.id,
            quantity=quantity,
            transaction_type='Stock Added',
            remarks='Initial stock entry on item creation'
        )
        db.session.add(history)
        db.session.commit()

        flash(f'Item "{item_name}" ({item_code}) added successfully!', 'success')
        return redirect(url_for('items_list'))

    today_str = date.today().isoformat()
    return render_template('add_item.html', categories=CATEGORIES, today=today_str)


@app.route('/admin/items/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('items_list'))

    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        item_code = request.form.get('item_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        minimum_stock = request.form.get('minimum_stock', type=int)
        unit = request.form.get('unit', '').strip()
        location = request.form.get('location', '').strip()

        if not item_name or not item_code or not category or minimum_stock is None or not unit or not location:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('edit_item', item_id=item_id))

        if minimum_stock < 0:
            flash('Minimum stock threshold cannot be negative.', 'danger')
            return redirect(url_for('edit_item', item_id=item_id))

        # Check unique code among other items
        existing = db.session.query(Item).filter(Item.item_code == item_code, Item.id != item_id).first()
        if existing:
            flash(f'Another item with Item Code "{item_code}" already exists.', 'danger')
            return redirect(url_for('edit_item', item_id=item_id))

        item.item_name = item_name
        item.item_code = item_code
        item.category = category
        item.minimum_stock = minimum_stock
        item.unit = unit
        item.location = location

        db.session.commit()
        flash(f'Item "{item.item_name}" details updated successfully!', 'success')
        return redirect(url_for('items_list'))

    return render_template('edit_item.html', item=item, categories=CATEGORIES)


@app.route('/admin/items/delete/<int:item_id>', methods=['POST'])
@admin_required
def delete_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('items_list'))

    item_name = item.item_name
    db.session.delete(item)
    db.session.commit()

    flash(f'Item "{item_name}" has been deleted.', 'info')
    return redirect(url_for('items_list'))


@app.route('/admin/stock/update', methods=['GET', 'POST'])
@admin_required
def stock_update():
    items = db.session.query(Item).order_by(Item.item_name.asc()).all()

    if request.method == 'POST':
        item_id = request.form.get('item_id', type=int)
        transaction_type = request.form.get('transaction_type', '').strip()
        quantity = request.form.get('quantity', type=int)
        remarks = request.form.get('remarks', '').strip()

        if not item_id or not transaction_type or quantity is None:
            flash('Please select an item, transaction type, and enter quantity.', 'danger')
            return redirect(url_for('stock_update'))

        if quantity <= 0:
            flash('Transaction quantity must be greater than zero.', 'danger')
            return redirect(url_for('stock_update'))

        item = db.session.get(Item, item_id)
        if not item:
            flash('Selected item not found.', 'danger')
            return redirect(url_for('stock_update'))

        if transaction_type == 'Stock Added':
            item.quantity += quantity
        elif transaction_type == 'Stock Used':
            if quantity > item.quantity:
                flash(f'Cannot reduce stock by {quantity}. Only {item.quantity} {item.unit} available in stock!', 'danger')
                return redirect(url_for('stock_update'))
            item.quantity -= quantity
        else:
            flash('Invalid transaction type.', 'danger')
            return redirect(url_for('stock_update'))

        # Record stock history
        history = StockHistory(
            item_id=item.id,
            quantity=quantity,
            transaction_type=transaction_type,
            remarks=remarks if remarks else f'{transaction_type} operation'
        )
        db.session.add(history)
        db.session.commit()

        flash(f'Stock updated successfully for "{item.item_name}". New Quantity: {item.quantity} {item.unit}.', 'success')
        return redirect(url_for('items_list'))

    selected_item_id = request.args.get('item_id', type=int)
    return render_template('stock_update.html', items=items, selected_item_id=selected_item_id)


@app.route('/admin/stock/history')
@admin_required
def stock_history():
    item_id = request.args.get('item_id', type=int)
    query = db.session.query(StockHistory).join(Item)

    if item_id:
        query = query.filter(StockHistory.item_id == item_id)

    history_logs = query.order_by(StockHistory.date.desc()).all()
    items = db.session.query(Item).order_by(Item.item_name.asc()).all()

    return render_template('stock_history.html', history_logs=history_logs, items=items, selected_item_id=item_id)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
