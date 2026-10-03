import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lab_consumables_secret_key_2025_mca')

# Database configuration: Default to MySQL URI, fallback for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/lab_consumables_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'lab_consumables.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Preset Categories
CATEGORIES = [
    'Chemicals',
    'Glassware',
    'Stationery',
    'Electronic Components',
    'Cleaning Materials',
    'Other'
]


# Database Models

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)


class Consumable(db.Model):
    __tablename__ = 'consumables'
    id = db.Column(db.Integer, primary_key=True)
    consumable_name = db.Column(db.String(100), nullable=False)
    item_code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False)
    lab_name = db.Column(db.String(100), nullable=False)
    added_date = db.Column(db.Date, nullable=False, default=date.today)

    history = db.relationship('StockHistory', backref='consumable', lazy=True, cascade='all, delete-orphan')

    @property
    def stock_status(self):
        if self.quantity == 0:
            return 'Out of Stock'
        elif self.quantity <= self.minimum_stock:
            return 'Low Stock'
        else:
            return 'In Stock'

    @property
    def badge_class(self):
        status = self.stock_status
        if status == 'In Stock':
            return 'bg-mint text-dark'
        elif status == 'Low Stock':
            return 'bg-warning text-dark'
        else:
            return 'bg-danger text-white'


class StockHistory(db.Model):
    __tablename__ = 'stock_history'
    id = db.Column(db.Integer, primary_key=True)
    consumable_id = db.Column(db.Integer, db.ForeignKey('consumables.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'Stock Added' or 'Stock Used'
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today)
    remarks = db.Column(db.String(255), nullable=True)


# Auth Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as Admin to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# Default Seeding
def seed_default_data():
    if Admin.query.count() == 0:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

    if Consumable.query.count() == 0:
        sample_consumables = [
            Consumable(
                consumable_name='Sodium Hydroxide Pellets',
                item_code='CHEM-101',
                category='Chemicals',
                quantity=25,
                minimum_stock=10,
                unit='Kg',
                lab_name='Chemistry Lab',
                added_date=date(2025, 1, 10)
            ),
            Consumable(
                consumable_name='Glass Beaker 250ml',
                item_code='GLAS-201',
                category='Glassware',
                quantity=3,
                minimum_stock=10,
                unit='Pieces',
                lab_name='Chemistry Lab',
                added_date=date(2025, 1, 12)
            ),
            Consumable(
                consumable_name='A4 Printing Paper',
                item_code='STAT-301',
                category='Stationery',
                quantity=0,
                minimum_stock=5,
                unit='Reams',
                lab_name='Computer Lab 1',
                added_date=date(2025, 1, 15)
            ),
            Consumable(
                consumable_name='Resistor Pack 10k Ohm',
                item_code='ELEC-401',
                category='Electronic Components',
                quantity=100,
                minimum_stock=25,
                unit='Packs',
                lab_name='Electronics Lab',
                added_date=date(2025, 1, 18)
            ),
            Consumable(
                consumable_name='Ethanol 99% Pure',
                item_code='CHEM-102',
                category='Chemicals',
                quantity=4,
                minimum_stock=5,
                unit='Bottles',
                lab_name='Chemistry Lab',
                added_date=date(2025, 1, 20)
            ),
            Consumable(
                consumable_name='Microfiber Cloth',
                item_code='CLEN-501',
                category='Cleaning Materials',
                quantity=15,
                minimum_stock=5,
                unit='Packs',
                lab_name='Hardware Lab',
                added_date=date(2025, 1, 22)
            )
        ]
        db.session.add_all(sample_consumables)
        db.session.commit()

        history_records = [
            StockHistory(consumable_id=1, transaction_type='Stock Added', quantity=25, transaction_date=date(2025, 1, 10), remarks='Initial stock purchase'),
            StockHistory(consumable_id=2, transaction_type='Stock Added', quantity=15, transaction_date=date(2025, 1, 12), remarks='Initial stock purchase'),
            StockHistory(consumable_id=2, transaction_type='Stock Used', quantity=12, transaction_date=date(2025, 1, 14), remarks='Used in Organic Chemistry experiment'),
            StockHistory(consumable_id=3, transaction_type='Stock Added', quantity=10, transaction_date=date(2025, 1, 15), remarks='Monthly supply'),
            StockHistory(consumable_id=3, transaction_type='Stock Used', quantity=10, transaction_date=date(2025, 1, 25), remarks='Exam paper printing'),
            StockHistory(consumable_id=4, transaction_type='Stock Added', quantity=100, transaction_date=date(2025, 1, 18), remarks='Bulk purchase for lab practicals')
        ]
        db.session.add_all(history_records)
        db.session.commit()


# Application Routes

@app.route('/')
def index():
    total_items = Consumable.query.count()
    low_stock_items = sum(1 for c in Consumable.query.all() if c.stock_status == 'Low Stock')
    out_of_stock_items = sum(1 for c in Consumable.query.all() if c.stock_status == 'Out of Stock')
    in_stock_items = sum(1 for c in Consumable.query.all() if c.stock_status == 'In Stock')
    return render_template(
        'index.html',
        total_items=total_items,
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        in_stock_items=in_stock_items
    )


@app.route('/login', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Both username and password are required.', 'danger')
            return redirect(url_for('admin_login'))

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            flash(f'Welcome back, {admin.username}! Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@admin_required
def dashboard():
    all_consumables = Consumable.query.all()
    total_consumables = len(all_consumables)
    available_stock = sum(c.quantity for c in all_consumables)
    low_stock_items = [c for c in all_consumables if c.stock_status == 'Low Stock']
    out_of_stock_items = [c for c in all_consumables if c.stock_status == 'Out of Stock']

    recent_history = StockHistory.query.order_by(StockHistory.transaction_date.desc(), StockHistory.id.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_consumables=total_consumables,
        available_stock=available_stock,
        low_stock_count=len(low_stock_items),
        out_of_stock_count=len(out_of_stock_items),
        low_stock_items=low_stock_items,
        out_of_stock_items=out_of_stock_items,
        recent_history=recent_history
    )


@app.route('/consumables')
@admin_required
def consumables():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Consumable.query

    if search_query:
        query = query.filter(
            (Consumable.consumable_name.ilike(f'%{search_query}%')) |
            (Consumable.item_code.ilike(f'%{search_query}%'))
        )

    if category_filter and category_filter != 'All':
        query = query.filter(Consumable.category == category_filter)

    all_matching = query.order_by(Consumable.consumable_name.asc()).all()

    # Apply status filter in python property
    if status_filter and status_filter != 'All':
        all_matching = [c for c in all_matching if c.stock_status == status_filter]

    return render_template(
        'consumables.html',
        consumables=all_matching,
        categories=CATEGORIES,
        search_query=search_query,
        category_filter=category_filter,
        status_filter=status_filter
    )


@app.route('/consumables/add', methods=['GET', 'POST'])
@admin_required
def add_consumable():
    if request.method == 'POST':
        consumable_name = request.form.get('consumable_name', '').strip()
        item_code = request.form.get('item_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        quantity_str = request.form.get('quantity', '0').strip()
        minimum_stock_str = request.form.get('minimum_stock', '0').strip()
        unit = request.form.get('unit', '').strip()
        lab_name = request.form.get('lab_name', '').strip()
        added_date_str = request.form.get('added_date', '').strip()

        if not consumable_name or not item_code or not category or not unit or not lab_name:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('add_consumable'))

        try:
            quantity = int(quantity_str)
            minimum_stock = int(minimum_stock_str)
            if quantity < 0 or minimum_stock < 0:
                raise ValueError()
        except ValueError:
            flash('Quantity and Minimum Stock Level must be non-negative numbers.', 'danger')
            return redirect(url_for('add_consumable'))

        if Consumable.query.filter_by(item_code=item_code).first():
            flash(f'An item with Item Code "{item_code}" already exists.', 'danger')
            return redirect(url_for('add_consumable'))

        try:
            added_date = datetime.strptime(added_date_str, '%Y-%m-%d').date() if added_date_str else date.today()
        except ValueError:
            added_date = date.today()

        consumable = Consumable(
            consumable_name=consumable_name,
            item_code=item_code,
            category=category,
            quantity=quantity,
            minimum_stock=minimum_stock,
            unit=unit,
            lab_name=lab_name,
            added_date=added_date
        )
        db.session.add(consumable)
        db.session.commit()

        # Log initial stock in history if initial quantity > 0
        if quantity > 0:
            history = StockHistory(
                consumable_id=consumable.id,
                transaction_type='Stock Added',
                quantity=quantity,
                transaction_date=added_date,
                remarks='Initial stock recorded upon creation'
            )
            db.session.add(history)
            db.session.commit()

        flash(f'Consumable "{consumable_name}" ({item_code}) added successfully!', 'success')
        return redirect(url_for('consumables'))

    today_str = date.today().isoformat()
    return render_template('add_consumable.html', categories=CATEGORIES, today=today_str)


@app.route('/consumables/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_consumable(id):
    consumable = Consumable.query.get_or_404(id)

    if request.method == 'POST':
        consumable_name = request.form.get('consumable_name', '').strip()
        item_code = request.form.get('item_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        minimum_stock_str = request.form.get('minimum_stock', '0').strip()
        unit = request.form.get('unit', '').strip()
        lab_name = request.form.get('lab_name', '').strip()

        if not consumable_name or not item_code or not category or not unit or not lab_name:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('edit_consumable', id=id))

        try:
            minimum_stock = int(minimum_stock_str)
            if minimum_stock < 0:
                raise ValueError()
        except ValueError:
            flash('Minimum Stock Level must be a non-negative number.', 'danger')
            return redirect(url_for('edit_consumable', id=id))

        # Check unique code
        existing = Consumable.query.filter(Consumable.item_code == item_code, Consumable.id != id).first()
        if existing:
            flash(f'Item Code "{item_code}" is already in use by another consumable.', 'danger')
            return redirect(url_for('edit_consumable', id=id))

        consumable.consumable_name = consumable_name
        consumable.item_code = item_code
        consumable.category = category
        consumable.minimum_stock = minimum_stock
        consumable.unit = unit
        consumable.lab_name = lab_name

        db.session.commit()
        flash(f'Consumable "{consumable_name}" updated successfully.', 'success')
        return redirect(url_for('consumables'))

    return render_template('edit_consumable.html', consumable=consumable, categories=CATEGORIES)


@app.route('/consumables/delete/<int:id>', methods=['POST'])
@admin_required
def delete_consumable(id):
    consumable = Consumable.query.get_or_404(id)
    name = consumable.consumable_name
    db.session.delete(consumable)
    db.session.commit()
    flash(f'Consumable "{name}" deleted successfully.', 'info')
    return redirect(url_for('consumables'))


@app.route('/stock/update', methods=['GET', 'POST'])
@admin_required
def stock_update():
    preselect_id = request.args.get('consumable_id', type=int)

    if request.method == 'POST':
        consumable_id = request.form.get('consumable_id', type=int)
        action_type = request.form.get('action_type', '').strip()  # 'add' or 'use'
        quantity_str = request.form.get('quantity', '0').strip()
        transaction_date_str = request.form.get('transaction_date', '').strip()
        remarks = request.form.get('remarks', '').strip()

        if not consumable_id or not action_type or action_type not in ['add', 'use']:
            flash('Please select a valid consumable and transaction type.', 'danger')
            return redirect(url_for('stock_update', consumable_id=consumable_id))

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                raise ValueError()
        except ValueError:
            flash('Quantity must be a positive integer greater than zero.', 'danger')
            return redirect(url_for('stock_update', consumable_id=consumable_id))

        try:
            trans_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date() if transaction_date_str else date.today()
        except ValueError:
            trans_date = date.today()

        consumable = Consumable.query.get_or_404(consumable_id)

        if action_type == 'use':
            if quantity > consumable.quantity:
                flash(
                    f'Cannot deduct {quantity} {consumable.unit}! Current available stock for "{consumable.consumable_name}" is only {consumable.quantity} {consumable.unit}. Negative stock is not allowed.',
                    'danger'
                )
                return redirect(url_for('stock_update', consumable_id=consumable_id))

            consumable.quantity -= quantity
            trans_type = 'Stock Used'
            flash_msg = f'Successfully deducted {quantity} {consumable.unit} from "{consumable.consumable_name}". New stock: {consumable.quantity} {consumable.unit}.'
        else:
            consumable.quantity += quantity
            trans_type = 'Stock Added'
            flash_msg = f'Successfully added {quantity} {consumable.unit} to "{consumable.consumable_name}". New stock: {consumable.quantity} {consumable.unit}.'

        history = StockHistory(
            consumable_id=consumable.id,
            transaction_type=trans_type,
            quantity=quantity,
            transaction_date=trans_date,
            remarks=remarks if remarks else f'Stock {action_type.title()}ed via Stock Update form'
        )

        db.session.add(history)
        db.session.commit()

        flash(flash_msg, 'success')
        return redirect(url_for('stock_history'))

    consumables_list = Consumable.query.order_by(Consumable.consumable_name.asc()).all()
    today_str = date.today().isoformat()
    return render_template(
        'stock_update.html',
        consumables=consumables_list,
        preselect_id=preselect_id,
        today=today_str
    )


@app.route('/stock/history')
@admin_required
def stock_history():
    consumable_id = request.args.get('consumable_id', type=int)
    trans_type = request.args.get('transaction_type', '').strip()

    query = StockHistory.query

    if consumable_id:
        query = query.filter(StockHistory.consumable_id == consumable_id)

    if trans_type and trans_type != 'All':
        query = query.filter(StockHistory.transaction_type == trans_type)

    history_records = query.order_by(StockHistory.transaction_date.desc(), StockHistory.id.desc()).all()
    consumables_list = Consumable.query.order_by(Consumable.consumable_name.asc()).all()

    return render_template(
        'stock_history.html',
        history=history_records,
        consumables=consumables_list,
        selected_consumable_id=consumable_id,
        selected_trans_type=trans_type
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
