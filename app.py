import os
import random
import string
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'business_supplier_purchase_secret_key_98765')

# Database configuration: Default to MySQL URI, fallback/option for SQLite
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/supplier_purchase_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'supplier_purchase.db')

use_sqlite = os.environ.get('USE_SQLITE') == '1'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLITE_URI if use_sqlite else MYSQL_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active') # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchases = db.relationship('Purchase', backref='supplier', lazy=True, cascade='all, delete-orphan')

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    current_stock = db.Column(db.Integer, nullable=False, default=0)
    min_stock_level = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    purchase_items = db.relationship('PurchaseItem', backref='product', lazy=True)

    @property
    def stock_status(self):
        if self.current_stock == 0:
            return 'Out of Stock'
        elif self.current_stock <= self.min_stock_level:
            return 'Low Stock'
        return 'In Stock'

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    purchase_number = db.Column(db.String(50), unique=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Ordered, Received, Cancelled
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('PurchaseItem', backref='purchase', lazy=True, cascade='all, delete-orphan')

class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    purchase_price = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)

def generate_purchase_number():
    last_purchase = db.session.query(Purchase).order_by(Purchase.id.desc()).first()
    if last_purchase:
        next_id = last_purchase.id + 1001
    else:
        next_id = 1001
    pur_num = f"PUR-{next_id}"
    while db.session.query(Purchase).filter_by(purchase_number=pur_num).first() is not None:
        next_id += 1
        pur_num = f"PUR-{next_id}"
    return pur_num

def seed_default_data():
    if db.session.query(Admin).count() == 0:
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    if db.session.query(Supplier).count() == 0:
        s1 = Supplier(supplier_name='Rajesh Sharma', company_name='Apex Global Traders', phone='+91 9876543210', email='rajesh@apexglobal.com', address='123 Commercial Hub, MG Road, Mumbai', status='Active')
        s2 = Supplier(supplier_name='Priya Verma', company_name='Tech & Tools Supplies', phone='+91 9812345678', email='priya@techtools.com', address='45 Industrial Estate, Electronic City, Bengaluru', status='Active')
        s3 = Supplier(supplier_name='Suresh Kumar', company_name='Prime Logistics & Goods', phone='+91 9765432109', email='suresh@primelogistics.com', address='78 Warehouse Zone, GT Road, Delhi', status='Inactive')
        db.session.add_all([s1, s2, s3])
        db.session.commit()

    if db.session.query(Product).count() == 0:
        p1 = Product(product_name='Ergonomic Office Chair', product_code='PROD-101', category='Furniture', purchase_price=3500.0, current_stock=15, min_stock_level=5)
        p2 = Product(product_name='Wireless Mechanical Keyboard', product_code='PROD-102', category='Electronics', purchase_price=2200.0, current_stock=3, min_stock_level=10)
        p3 = Product(product_name='LED Desktop Monitor 24"', product_code='PROD-103', category='Electronics', purchase_price=8500.0, current_stock=0, min_stock_level=4)
        p4 = Product(product_name='Heavy Duty Storage Shelves', product_code='PROD-104', category='Equipment', purchase_price=4500.0, current_stock=25, min_stock_level=8)
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

    if db.session.query(Purchase).count() == 0:
        s1 = db.session.query(Supplier).filter_by(company_name='Apex Global Traders').first()
        s2 = db.session.query(Supplier).filter_by(company_name='Tech & Tools Supplies').first()
        p1 = db.session.query(Product).filter_by(product_code='PROD-101').first()
        p2 = db.session.query(Product).filter_by(product_code='PROD-102').first()
        p3 = db.session.query(Product).filter_by(product_code='PROD-103').first()

        if s1 and s2 and p1 and p2 and p3:
            pur1 = Purchase(purchase_number='PUR-1001', supplier_id=s1.id, purchase_date=date(2023, 10, 10), status='Received', total_amount=17500.0, notes='Initial stock purchase for office chairs')
            item1 = PurchaseItem(purchase=pur1, product_id=p1.id, quantity=5, purchase_price=3500.0, subtotal=17500.0)

            pur2 = Purchase(purchase_number='PUR-1002', supplier_id=s2.id, purchase_date=date(2023, 10, 15), status='Pending', total_amount=11000.0, notes='Awaiting approval for keyboards')
            item2 = PurchaseItem(purchase=pur2, product_id=p2.id, quantity=5, purchase_price=2200.0, subtotal=11000.0)

            pur3 = Purchase(purchase_number='PUR-1003', supplier_id=s1.id, purchase_date=date(2023, 10, 18), status='Ordered', total_amount=34000.0, notes='Monitors batch order placed with Apex Global')
            item3 = PurchaseItem(purchase=pur3, product_id=p3.id, quantity=4, purchase_price=8500.0, subtotal=34000.0)

            db.session.add_all([pur1, item1, pur2, item2, pur3, item3])
            db.session.commit()

# Auth Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session or not session['admin_logged_in']:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and Password are required.', 'danger')
            return render_template('login.html')

        admin = db.session.query(Admin).filter_by(username=username).first()

        if admin and admin.check_password(password):
            session['admin_logged_in'] = True
            session['admin_username'] = admin.username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('dashboard'))
        # Hardcoded fallback for easy testing if db not populated
        elif username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_username'] = 'admin'
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid admin credentials. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_suppliers = db.session.query(Supplier).count()
    total_products = db.session.query(Product).count()
    total_purchases = db.session.query(Purchase).count()
    pending_purchases = db.session.query(Purchase).filter_by(status='Pending').count()
    completed_purchases = db.session.query(Purchase).filter_by(status='Received').count()
    total_purchase_amount = db.session.query(db.func.sum(Purchase.total_amount)).scalar() or 0.0

    recent_purchases = db.session.query(Purchase).order_by(Purchase.created_at.desc()).limit(5).all()
    all_products = db.session.query(Product).all()
    low_stock_products = [p for p in all_products if p.stock_status in ['Low Stock', 'Out of Stock']]

    return render_template('dashboard.html',
                           total_suppliers=total_suppliers,
                           total_products=total_products,
                           total_purchases=total_purchases,
                           pending_purchases=pending_purchases,
                           completed_purchases=completed_purchases,
                           total_purchase_amount=total_purchase_amount,
                           recent_purchases=recent_purchases,
                           low_stock_products=low_stock_products)

# Supplier Management
@app.route('/suppliers')
@login_required
def suppliers():
    search_query = request.args.get('search', '').strip()
    query = db.session.query(Supplier)

    if search_query:
        query = query.filter(
            (Supplier.supplier_name.ilike(f'%{search_query}%')) |
            (Supplier.company_name.ilike(f'%{search_query}%')) |
            (Supplier.email.ilike(f'%{search_query}%')) |
            (Supplier.phone.ilike(f'%{search_query}%'))
        )

    supplier_list = query.order_by(Supplier.created_at.desc()).all()
    return render_template('suppliers.html', suppliers=supplier_list, search_query=search_query)

@app.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        supplier_name = request.form.get('supplier_name', '').strip()
        company_name = request.form.get('company_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        status = request.form.get('status', 'Active').strip()

        if not supplier_name or not company_name or not phone or not email:
            flash('Supplier Name, Company Name, Phone, and Email are required.', 'danger')
            return render_template('add_supplier.html')

        new_supplier = Supplier(
            supplier_name=supplier_name,
            company_name=company_name,
            phone=phone,
            email=email,
            address=address,
            status=status
        )
        db.session.add(new_supplier)
        db.session.commit()
        flash(f'Supplier "{company_name}" added successfully.', 'success')
        return redirect(url_for('suppliers'))

    return render_template('add_supplier.html')

@app.route('/suppliers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = db.session.get(Supplier, id)
    if not supplier:
        flash('Supplier not found.', 'danger')
        return redirect(url_for('suppliers'))

    if request.method == 'POST':
        supplier.supplier_name = request.form.get('supplier_name', '').strip()
        supplier.company_name = request.form.get('company_name', '').strip()
        supplier.phone = request.form.get('phone', '').strip()
        supplier.email = request.form.get('email', '').strip()
        supplier.address = request.form.get('address', '').strip()
        supplier.status = request.form.get('status', 'Active').strip()

        if not supplier.supplier_name or not supplier.company_name or not supplier.phone or not supplier.email:
            flash('Supplier Name, Company Name, Phone, and Email are required.', 'danger')
            return render_template('edit_supplier.html', supplier=supplier)

        db.session.commit()
        flash(f'Supplier "{supplier.company_name}" updated successfully.', 'success')
        return redirect(url_for('suppliers'))

    return render_template('edit_supplier.html', supplier=supplier)

@app.route('/suppliers/<int:id>')
@login_required
def supplier_details(id):
    supplier = db.session.get(Supplier, id)
    if not supplier:
        flash('Supplier not found.', 'danger')
        return redirect(url_for('suppliers'))

    supplier_purchases = db.session.query(Purchase).filter_by(supplier_id=supplier.id).order_by(Purchase.purchase_date.desc()).all()
    total_purchases_count = len(supplier_purchases)
    total_purchase_amount = sum(p.total_amount for p in supplier_purchases)

    return render_template('supplier_details.html',
                           supplier=supplier,
                           purchases=supplier_purchases,
                           total_purchases_count=total_purchases_count,
                           total_purchase_amount=total_purchase_amount)

@app.route('/suppliers/delete/<int:id>', methods=['POST'])
@login_required
def delete_supplier(id):
    supplier = db.session.get(Supplier, id)
    if supplier:
        name = supplier.company_name
        db.session.delete(supplier)
        db.session.commit()
        flash(f'Supplier "{name}" deleted successfully.', 'info')
    else:
        flash('Supplier not found.', 'danger')
    return redirect(url_for('suppliers'))

# Product Management
@app.route('/products')
@login_required
def products():
    search_query = request.args.get('search', '').strip()
    query = db.session.query(Product)

    if search_query:
        query = query.filter(
            (Product.product_name.ilike(f'%{search_query}%')) |
            (Product.product_code.ilike(f'%{search_query}%')) |
            (Product.category.ilike(f'%{search_query}%'))
        )

    product_list = query.order_by(Product.created_at.desc()).all()
    return render_template('products.html', products=product_list, search_query=search_query)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()
        product_code = request.form.get('product_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        purchase_price = request.form.get('purchase_price', type=float, default=0.0)
        current_stock = request.form.get('current_stock', type=int, default=0)
        min_stock_level = request.form.get('min_stock_level', type=int, default=5)

        if not product_name or not product_code or not category or purchase_price < 0 or current_stock < 0 or min_stock_level < 0:
            flash('All product fields are required and numeric values must be non-negative.', 'danger')
            return render_template('add_product.html')

        existing = db.session.query(Product).filter_by(product_code=product_code).first()
        if existing:
            flash(f'Product code "{product_code}" already exists. Please use a unique product code.', 'danger')
            return render_template('add_product.html')

        new_product = Product(
            product_name=product_name,
            product_code=product_code,
            category=category,
            purchase_price=purchase_price,
            current_stock=current_stock,
            min_stock_level=min_stock_level
        )
        db.session.add(new_product)
        db.session.commit()
        flash(f'Product "{product_name}" added successfully.', 'success')
        return redirect(url_for('products'))

    return render_template('add_product.html')

@app.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = db.session.get(Product, id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products'))

    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()
        product_code = request.form.get('product_code', '').strip().upper()
        category = request.form.get('category', '').strip()
        purchase_price = request.form.get('purchase_price', type=float, default=0.0)
        current_stock = request.form.get('current_stock', type=int, default=0)
        min_stock_level = request.form.get('min_stock_level', type=int, default=5)

        if not product_name or not product_code or not category or purchase_price < 0 or current_stock < 0 or min_stock_level < 0:
            flash('All product fields are required and must be valid.', 'danger')
            return render_template('edit_product.html', product=product)

        existing = db.session.query(Product).filter(Product.product_code == product_code, Product.id != id).first()
        if existing:
            flash(f'Product code "{product_code}" is already in use by another product.', 'danger')
            return render_template('edit_product.html', product=product)

        product.product_name = product_name
        product.product_code = product_code
        product.category = category
        product.purchase_price = purchase_price
        product.current_stock = current_stock
        product.min_stock_level = min_stock_level

        db.session.commit()
        flash(f'Product "{product_name}" updated successfully.', 'success')
        return redirect(url_for('products'))

    return render_template('edit_product.html', product=product)

@app.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = db.session.get(Product, id)
    if product:
        name = product.product_name
        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{name}" deleted successfully.', 'info')
    else:
        flash('Product not found.', 'danger')
    return redirect(url_for('products'))

# Purchase Management & History
@app.route('/purchases')
def purchases():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))

    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = db.session.query(Purchase).join(Supplier)

    if status_filter and status_filter != 'All':
        query = query.filter(Purchase.status == status_filter)

    if search_query:
        query = query.outerjoin(PurchaseItem).outerjoin(Product).filter(
            (Purchase.purchase_number.ilike(f'%{search_query}%')) |
            (Supplier.company_name.ilike(f'%{search_query}%')) |
            (Supplier.supplier_name.ilike(f'%{search_query}%')) |
            (Product.product_name.ilike(f'%{search_query}%'))
        )

    purchase_list = query.order_by(Purchase.purchase_date.desc(), Purchase.created_at.desc()).all()
    return render_template('purchases.html', purchases=purchase_list, search_query=search_query, status_filter=status_filter)

@app.route('/purchase-history')
@login_required
def purchase_history():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = db.session.query(Purchase).join(Supplier)

    if status_filter and status_filter != 'All':
        query = query.filter(Purchase.status == status_filter)

    if search_query:
        query = query.outerjoin(PurchaseItem).outerjoin(Product).filter(
            (Purchase.purchase_number.ilike(f'%{search_query}%')) |
            (Supplier.company_name.ilike(f'%{search_query}%')) |
            (Supplier.supplier_name.ilike(f'%{search_query}%')) |
            (Product.product_name.ilike(f'%{search_query}%'))
        )

    purchase_list = query.order_by(Purchase.purchase_date.desc(), Purchase.created_at.desc()).all()
    return render_template('purchase_history.html', purchases=purchase_list, search_query=search_query, status_filter=status_filter)

@app.route('/purchases/add', methods=['GET', 'POST'])
@login_required
def add_purchase():
    if request.method == 'POST':
        purchase_number = request.form.get('purchase_number', '').strip()
        supplier_id = request.form.get('supplier_id', type=int)
        product_id = request.form.get('product_id', type=int)
        purchase_date_str = request.form.get('purchase_date', '')
        quantity = request.form.get('quantity', type=int, default=1)
        purchase_price = request.form.get('purchase_price', type=float, default=0.0)
        status = request.form.get('status', 'Pending').strip()
        notes = request.form.get('notes', '').strip()

        if not purchase_number or not supplier_id or not product_id or quantity <= 0 or purchase_price < 0:
            flash('Valid Purchase Number, Supplier, Product, Quantity (>0), and Price are required.', 'danger')
            suppliers_active = db.session.query(Supplier).filter_by(status='Active').all()
            products_all = db.session.query(Product).all()
            return render_template('add_purchase.html', auto_pur_num=generate_purchase_number(), suppliers=suppliers_active, products=products_all, today=date.today().isoformat())

        try:
            purchase_date_obj = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else date.today()
        except ValueError:
            purchase_date_obj = date.today()

        total_amount = round(quantity * purchase_price, 2)

        purchase = Purchase(
            purchase_number=purchase_number,
            supplier_id=supplier_id,
            purchase_date=purchase_date_obj,
            status=status,
            total_amount=total_amount,
            notes=notes
        )

        item = PurchaseItem(
            purchase=purchase,
            product_id=product_id,
            quantity=quantity,
            purchase_price=purchase_price,
            subtotal=total_amount
        )

        db.session.add(purchase)
        db.session.add(item)

        # Automatic Stock Increment if status is 'Received'
        if status == 'Received':
            product = db.session.get(Product, product_id)
            if product:
                product.current_stock += quantity

        db.session.commit()
        flash(f'Purchase "{purchase_number}" created successfully!', 'success')
        return redirect(url_for('purchases'))

    suppliers_active = db.session.query(Supplier).filter_by(status='Active').all()
    products_all = db.session.query(Product).all()
    auto_pur_num = generate_purchase_number()
    today_str = date.today().isoformat()

    return render_template('add_purchase.html',
                           auto_pur_num=auto_pur_num,
                           suppliers=suppliers_active,
                           products=products_all,
                           today=today_str)

@app.route('/purchases/<int:id>')
@login_required
def purchase_details(id):
    purchase = db.session.get(Purchase, id)
    if not purchase:
        flash('Purchase record not found.', 'danger')
        return redirect(url_for('purchases'))

    return render_template('purchase_details.html', purchase=purchase)

@app.route('/purchases/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_purchase(id):
    purchase = db.session.get(Purchase, id)
    if not purchase:
        flash('Purchase record not found.', 'danger')
        return redirect(url_for('purchases'))

    first_item = purchase.items[0] if purchase.items else None

    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id', type=int)
        product_id = request.form.get('product_id', type=int)
        purchase_date_str = request.form.get('purchase_date', '')
        quantity = request.form.get('quantity', type=int, default=1)
        purchase_price = request.form.get('purchase_price', type=float, default=0.0)
        new_status = request.form.get('status', 'Pending').strip()
        notes = request.form.get('notes', '').strip()

        if not supplier_id or not product_id or quantity <= 0 or purchase_price < 0:
            flash('All required fields must be properly specified.', 'danger')
            suppliers_active = db.session.query(Supplier).all()
            products_all = db.session.query(Product).all()
            return render_template('edit_purchase.html', purchase=purchase, suppliers=suppliers_active, products=products_all)

        try:
            purchase_date_obj = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else purchase.purchase_date
        except ValueError:
            purchase_date_obj = purchase.purchase_date

        old_status = purchase.status
        old_product_id = first_item.product_id if first_item else None
        old_quantity = first_item.quantity if first_item else 0

        total_amount = round(quantity * purchase_price, 2)
        purchase.supplier_id = supplier_id
        purchase.purchase_date = purchase_date_obj
        purchase.total_amount = total_amount
        purchase.notes = notes
        purchase.status = new_status

        if first_item:
            first_item.product_id = product_id
            first_item.quantity = quantity
            first_item.purchase_price = purchase_price
            first_item.subtotal = total_amount

        # Revert/apply stock changes accurately
        # 1. If previously 'Received', deduct the old stock from the old product
        if old_status == 'Received' and old_product_id:
            old_product = db.session.get(Product, old_product_id)
            if old_product:
                old_product.current_stock = max(0, old_product.current_stock - old_quantity)

        # 2. If new status is 'Received', add the new quantity to the new product
        if new_status == 'Received' and product_id:
            new_product = db.session.get(Product, product_id)
            if new_product:
                new_product.current_stock += quantity

        db.session.commit()
        flash(f'Purchase "{purchase.purchase_number}" updated successfully.', 'success')
        return redirect(url_for('purchases'))

    suppliers_active = db.session.query(Supplier).all()
    products_all = db.session.query(Product).all()
    return render_template('edit_purchase.html', purchase=purchase, suppliers=suppliers_active, products=products_all, item=first_item)

@app.route('/purchases/status-update/<int:id>', methods=['POST'])
@login_required
def update_purchase_status(id):
    purchase = db.session.get(Purchase, id)
    if not purchase:
        flash('Purchase record not found.', 'danger')
        return redirect(url_for('purchases'))

    new_status = request.form.get('status', '').strip()
    valid_statuses = ['Pending', 'Ordered', 'Received', 'Cancelled']

    if new_status not in valid_statuses:
        flash('Invalid purchase status.', 'danger')
        return redirect(url_for('purchases'))

    old_status = purchase.status
    if old_status == new_status:
        flash(f'Purchase status is already {new_status}.', 'info')
        return redirect(url_for('purchases'))

    purchase.status = new_status

    # Stock update logic
    for item in purchase.items:
        product = db.session.get(Product, item.product_id)
        if product:
            if old_status != 'Received' and new_status == 'Received':
                # Mark as Received -> Add stock
                product.current_stock += item.quantity
            elif old_status == 'Received' and new_status != 'Received':
                # Unmark Received -> Remove stock
                product.current_stock = max(0, product.current_stock - item.quantity)

    db.session.commit()
    flash(f'Status for purchase {purchase.purchase_number} updated to "{new_status}". Stock level updated automatically.', 'success')

    # Return to referer if available or purchases list
    return redirect(request.referrer or url_for('purchases'))

@app.route('/purchases/delete/<int:id>', methods=['POST'])
@login_required
def delete_purchase(id):
    purchase = db.session.get(Purchase, id)
    if purchase:
        # If purchase was 'Received', adjust stock
        if purchase.status == 'Received':
            for item in purchase.items:
                product = db.session.get(Product, item.product_id)
                if product:
                    product.current_stock = max(0, product.current_stock - item.quantity)

        num = purchase.purchase_number
        db.session.delete(purchase)
        db.session.commit()
        flash(f'Purchase record "{num}" deleted successfully.', 'info')
    else:
        flash('Purchase record not found.', 'danger')
    return redirect(url_for('purchases'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True, port=5000)
