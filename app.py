import os
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'small_business_sales_secret_key_12345')

# Admin Hardcoded Fallback Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/service_booking_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sales_management.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False, default='Administrator')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.Text, nullable=False)
    customer_type = db.Column(db.String(20), nullable=False, default='New')  # New, Regular, VIP
    registration_date = db.Column(db.Date, nullable=False, default=date.today)

    sales = db.relationship('Sale', backref='customer', lazy=True, cascade='all, delete-orphan')


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    selling_price = db.Column(db.Float, nullable=False, default=0.0)
    available_stock = db.Column(db.Integer, nullable=False, default=0)
    min_stock_level = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sale_items = db.relationship('SaleItem', backref='product', lazy=True)

    @property
    def stock_status(self):
        if self.available_stock <= 0:
            return 'Out of Stock'
        elif self.available_stock <= self.min_stock_level:
            return 'Low Stock'
        else:
            return 'In Stock'


class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    discount = db.Column(db.Float, nullable=False, default=0.0)
    grand_total = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.String(20), nullable=False, default='Paid')  # Paid, Partially Paid, Unpaid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')


class SaleItem(db.Model):
    __tablename__ = 'sale_items'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    total_price = db.Column(db.Float, nullable=False, default=0.0)


def generate_sale_number():
    today_str = date.today().strftime('%Y%m%d')
    latest_sale = Sale.query.order_by(Sale.id.desc()).first()
    if not latest_sale:
        return f"SL-{today_str}-0001"
    next_id = latest_sale.id + 1
    return f"SL-{today_str}-{next_id:04d}"


def seed_default_data():
    # Create default admin if not exists
    if Admin.query.count() == 0:
        admin = Admin(username=ADMIN_USERNAME, name='System Administrator')
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)

    # Seed default products
    if Product.query.count() == 0:
        products = [
            Product(name='Wireless Ergonomic Mouse', product_code='PRD-1001', category='Electronics', selling_price=799.0, available_stock=25, min_stock_level=5),
            Product(name='Mechanical RGB Keyboard', product_code='PRD-1002', category='Electronics', selling_price=2499.0, available_stock=12, min_stock_level=3),
            Product(name='USB-C Fast Charger 65W', product_code='PRD-1003', category='Accessories', selling_price=1299.0, available_stock=4, min_stock_level=5),
            Product(name='Noise Cancelling Headphones', product_code='PRD-1004', category='Audio', selling_price=3999.0, available_stock=0, min_stock_level=2),
            Product(name='Stainless Steel Water Bottle', product_code='PRD-1005', category='Home & Office', selling_price=499.0, available_stock=30, min_stock_level=8),
        ]
        db.session.add_all(products)

    # Seed default customers
    if Customer.query.count() == 0:
        customers = [
            Customer(name='Rahul Sharma', phone='9876543210', email='rahul@example.com', address='123 Main Street, City', customer_type='Regular'),
            Customer(name='Priya Patel', phone='9812345678', email='priya@example.com', address='45 Park View, City', customer_type='VIP'),
            Customer(name='Ankit Kumar', phone='9765432109', email='ankit@example.com', address='78 Market Road, City', customer_type='New'),
        ]
        db.session.add_all(customers)

    db.session.commit()


# Auth Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Please log in as Administrator to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Routes

@app.route('/')
def index():
    if session.get('user_type') == 'admin':
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Check in Database first
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['user_type'] = 'admin'
            session['user_id'] = admin.id
            session['user_name'] = admin.name
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('dashboard'))
        # Hardcoded fallback check
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['user_type'] = 'admin'
            session['user_id'] = 1
            session['user_name'] = 'Administrator'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@admin_required
def dashboard():
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_sales_count = Sale.query.count()

    today_date = date.today()
    sales_today = Sale.query.filter(Sale.sale_date == today_date).all()
    today_sales_count = len(sales_today)
    today_sales_revenue = sum(s.grand_total for s in sales_today)

    pending_orders_count = Sale.query.filter(Sale.payment_status.in_(['Unpaid', 'Partially Paid'])).count()

    all_sales = Sale.query.all()
    total_revenue = sum(s.grand_total for s in all_sales)

    # Sales Summary metrics
    start_of_week = today_date - timedelta(days=today_date.weekday())
    sales_this_week = Sale.query.filter(Sale.sale_date >= start_of_week).all()
    week_sales_revenue = sum(s.grand_total for s in sales_this_week)

    start_of_month = date(today_date.year, today_date.month, 1)
    sales_this_month = Sale.query.filter(Sale.sale_date >= start_of_month).all()
    month_sales_revenue = sum(s.grand_total for s in sales_this_month)

    recent_sales = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_customers=total_customers,
        total_products=total_products,
        total_sales_count=total_sales_count,
        today_sales_count=today_sales_count,
        today_sales_revenue=today_sales_revenue,
        pending_orders_count=pending_orders_count,
        total_revenue=total_revenue,
        week_sales_revenue=week_sales_revenue,
        month_sales_revenue=month_sales_revenue,
        recent_sales=recent_sales
    )


# Customer Management

@app.route('/customers')
@admin_required
def customers():
    search_query = request.args.get('search', '').strip()
    if search_query:
        search_filter = f"%{search_query}%"
        customer_list = Customer.query.filter(
            (Customer.name.ilike(search_filter)) |
            (Customer.phone.ilike(search_filter)) |
            (Customer.email.ilike(search_filter)) |
            (Customer.customer_type.ilike(search_filter))
        ).order_by(Customer.id.desc()).all()
    else:
        customer_list = Customer.query.order_by(Customer.id.desc()).all()

    return render_template('customers.html', customers=customer_list, search_query=search_query)


@app.route('/customers/add', methods=['GET', 'POST'])
@admin_required
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        customer_type = request.form.get('customer_type', 'New').strip()

        if not name or not phone or not email or not address:
            flash('All customer fields are required.', 'danger')
            return render_template('add_customer.html')

        customer = Customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            customer_type=customer_type,
            registration_date=date.today()
        )
        db.session.add(customer)
        db.session.commit()

        flash(f'Customer "{name}" added successfully.', 'success')
        return redirect(url_for('customers'))

    return render_template('add_customer.html')


@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
@admin_required
def edit_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        customer_type = request.form.get('customer_type', 'New').strip()

        if not name or not phone or not email or not address:
            flash('All customer fields are required.', 'danger')
            return render_template('edit_customer.html', customer=customer)

        customer.name = name
        customer.phone = phone
        customer.email = email
        customer.address = address
        customer.customer_type = customer_type

        db.session.commit()
        flash(f'Customer "{name}" updated successfully.', 'success')
        return redirect(url_for('customers'))

    return render_template('edit_customer.html', customer=customer)


@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
@admin_required
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    if customer:
        name = customer.name
        db.session.delete(customer)
        db.session.commit()
        flash(f'Customer "{name}" deleted successfully.', 'info')
    else:
        flash('Customer not found.', 'danger')
    return redirect(url_for('customers'))


@app.route('/customers/view/<int:customer_id>')
@admin_required
def customer_details(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        flash('Customer not found.', 'danger')
        return redirect(url_for('customers'))

    sales_history = Sale.query.filter_by(customer_id=customer_id).order_by(Sale.sale_date.desc(), Sale.id.desc()).all()
    total_purchases = len(sales_history)
    total_spent = sum(s.grand_total for s in sales_history)
    last_purchase_date = sales_history[0].sale_date if sales_history else None

    return render_template(
        'customer_details.html',
        customer=customer,
        sales_history=sales_history,
        total_purchases=total_purchases,
        total_spent=total_spent,
        last_purchase_date=last_purchase_date
    )


# Product Management

@app.route('/products')
@admin_required
def products():
    search_query = request.args.get('search', '').strip()
    if search_query:
        search_filter = f"%{search_query}%"
        product_list = Product.query.filter(
            (Product.name.ilike(search_filter)) |
            (Product.product_code.ilike(search_filter)) |
            (Product.category.ilike(search_filter))
        ).order_by(Product.id.desc()).all()
    else:
        product_list = Product.query.order_by(Product.id.desc()).all()

    return render_template('products.html', products=product_list, search_query=search_query)


@app.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        product_code = request.form.get('product_code', '').strip()
        category = request.form.get('category', '').strip()
        selling_price = request.form.get('selling_price', type=float, default=0.0)
        available_stock = request.form.get('available_stock', type=int, default=0)
        min_stock_level = request.form.get('min_stock_level', type=int, default=5)

        if not name or not product_code or not category or selling_price < 0 or available_stock < 0:
            flash('Please enter valid product details.', 'danger')
            return render_template('add_product.html')

        existing_product = Product.query.filter_by(product_code=product_code).first()
        if existing_product:
            flash(f'Product code "{product_code}" already exists.', 'danger')
            return render_template('add_product.html')

        product = Product(
            name=name,
            product_code=product_code,
            category=category,
            selling_price=selling_price,
            available_stock=available_stock,
            min_stock_level=min_stock_level
        )
        db.session.add(product)
        db.session.commit()

        flash(f'Product "{name}" added successfully.', 'success')
        return redirect(url_for('products'))

    return render_template('add_product.html')


@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        product_code = request.form.get('product_code', '').strip()
        category = request.form.get('category', '').strip()
        selling_price = request.form.get('selling_price', type=float, default=0.0)
        available_stock = request.form.get('available_stock', type=int, default=0)
        min_stock_level = request.form.get('min_stock_level', type=int, default=5)

        if not name or not product_code or not category or selling_price < 0 or available_stock < 0:
            flash('Please enter valid product details.', 'danger')
            return render_template('edit_product.html', product=product)

        # Check duplicate code if changed
        existing_product = Product.query.filter(Product.product_code == product_code, Product.id != product_id).first()
        if existing_product:
            flash(f'Product code "{product_code}" is already used by another product.', 'danger')
            return render_template('edit_product.html', product=product)

        product.name = name
        product.product_code = product_code
        product.category = category
        product.selling_price = selling_price
        product.available_stock = available_stock
        product.min_stock_level = min_stock_level

        db.session.commit()
        flash(f'Product "{name}" updated successfully.', 'success')
        return redirect(url_for('products'))

    return render_template('edit_product.html', product=product)


@app.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product:
        # Check if product is in sales
        associated_items = SaleItem.query.filter_by(product_id=product_id).first()
        if associated_items:
            flash(f'Cannot delete product "{product.name}" because it is linked to existing sales records.', 'warning')
        else:
            name = product.name
            db.session.delete(product)
            db.session.commit()
            flash(f'Product "{name}" deleted successfully.', 'info')
    else:
        flash('Product not found.', 'danger')
    return redirect(url_for('products'))


# Sales Management & History

@app.route('/sales')
@app.route('/sales/history')
@admin_required
def sales_history():
    search_query = request.args.get('search', '').strip()
    date_filter = request.args.get('date', '').strip()

    query = Sale.query.join(Customer)

    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            (Sale.sale_number.ilike(search_pattern)) |
            (Customer.name.ilike(search_pattern))
        )

    if date_filter:
        try:
            filter_d = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Sale.sale_date == filter_d)
        except ValueError:
            flash('Invalid date filter format.', 'warning')

    sales_list = query.order_by(Sale.id.desc()).all()

    return render_template(
        'sales_history.html',
        sales=sales_list,
        search_query=search_query,
        date_filter=date_filter
    )


@app.route('/sales/create', methods=['GET', 'POST'])
@admin_required
def create_sale():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        product_id = request.form.get('product_id', type=int)
        quantity = request.form.get('quantity', type=int, default=1)
        selling_price = request.form.get('selling_price', type=float, default=0.0)
        discount = request.form.get('discount', type=float, default=0.0)
        payment_status = request.form.get('payment_status', 'Paid').strip()
        sale_date_str = request.form.get('sale_date', date.today().isoformat())

        if not customer_id or not product_id or quantity <= 0 or selling_price < 0 or discount < 0:
            flash('Please enter valid sale details.', 'danger')
            return redirect(url_for('create_sale'))

        customer = db.session.get(Customer, customer_id)
        product = db.session.get(Product, product_id)

        if not customer or not product:
            flash('Selected customer or product does not exist.', 'danger')
            return redirect(url_for('create_sale'))

        # Stock check
        if product.available_stock < quantity:
            flash(f'Insufficient stock for "{product.name}". Available stock: {product.available_stock}, Requested: {quantity}.', 'danger')
            return redirect(url_for('create_sale'))

        try:
            sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date()
        except ValueError:
            sale_date = date.today()

        subtotal = quantity * selling_price
        grand_total = max(0.0, subtotal - discount)
        sale_num = generate_sale_number()

        # Reduce Stock
        product.available_stock -= quantity

        sale = Sale(
            sale_number=sale_num,
            customer_id=customer_id,
            sale_date=sale_date,
            total_amount=subtotal,
            discount=discount,
            grand_total=grand_total,
            payment_status=payment_status
        )
        db.session.add(sale)
        db.session.flush()  # to get sale.id

        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=product_id,
            quantity=quantity,
            unit_price=selling_price,
            total_price=subtotal
        )
        db.session.add(sale_item)
        db.session.commit()

        flash(f'Sale "{sale_num}" created successfully. Product stock updated.', 'success')
        return redirect(url_for('sale_details', sale_id=sale.id))

    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.order_by(Product.name).all()
    auto_sale_number = generate_sale_number()
    today_str = date.today().isoformat()

    return render_template(
        'create_sale.html',
        customers=customers,
        products=products,
        auto_sale_number=auto_sale_number,
        today=today_str
    )


@app.route('/sales/view/<int:sale_id>')
@admin_required
def sale_details(sale_id):
    sale = db.session.get(Sale, sale_id)
    if not sale:
        flash('Sale record not found.', 'danger')
        return redirect(url_for('sales_history'))

    return render_template('sale_details.html', sale=sale)


@app.route('/sales/edit/<int:sale_id>', methods=['GET', 'POST'])
@admin_required
def edit_sale(sale_id):
    sale = db.session.get(Sale, sale_id)
    if not sale:
        flash('Sale record not found.', 'danger')
        return redirect(url_for('sales_history'))

    if request.method == 'POST':
        payment_status = request.form.get('payment_status', sale.payment_status).strip()
        discount = request.form.get('discount', type=float, default=sale.discount)

        if discount < 0:
            flash('Discount cannot be negative.', 'danger')
            return redirect(url_for('edit_sale', sale_id=sale_id))

        sale.payment_status = payment_status
        sale.discount = discount
        sale.grand_total = max(0.0, sale.total_amount - discount)

        db.session.commit()
        flash(f'Sale "{sale.sale_number}" updated successfully.', 'success')
        return redirect(url_for('sale_details', sale_id=sale.id))

    return render_template('edit_sale.html', sale=sale)


@app.route('/sales/delete/<int:sale_id>', methods=['POST'])
@admin_required
def delete_sale(sale_id):
    sale = db.session.get(Sale, sale_id)
    if sale:
        sale_num = sale.sale_number
        # Restore stock for products in the sale
        for item in sale.items:
            product = db.session.get(Product, item.product_id)
            if product:
                product.available_stock += item.quantity

        db.session.delete(sale)
        db.session.commit()
        flash(f'Sale "{sale_num}" deleted and product stock restored.', 'info')
    else:
        flash('Sale record not found.', 'danger')

    return redirect(url_for('sales_history'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
