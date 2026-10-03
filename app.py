import os
import random
import string
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'small_business_enquiry_secret_key_2025')

# Admin Hardcoded Credentials
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database configuration: Default to MySQL URI, fallback to SQLite when USE_SQLITE=1
MYSQL_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost/small_business_db')
SQLITE_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'small_business.db')

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

class Enquiry(db.Model):
    __tablename__ = 'enquiries'
    id = db.Column(db.Integer, primary_key=True)
    ref_num = db.Column(db.String(20), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    enquiry_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), nullable=False, default='New') # New, In Progress, Responded, Closed
    admin_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leads = db.relationship('Lead', backref='enquiry', lazy=True)

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    enquiry_id = db.Column(db.Integer, db.ForeignKey('enquiries.id', ondelete='SET NULL'), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    requirement = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default='New Lead') # New Lead, Contacted, Follow-up, Converted, Lost
    follow_up_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    followups = db.relationship('FollowUp', backref='lead', lazy=True, cascade="all, delete-orphan")

class FollowUp(db.Model):
    __tablename__ = 'followups'
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.Integer, db.ForeignKey('leads.id', ondelete='CASCADE'), nullable=False)
    follow_up_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=False)
    status_at_time = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def generate_ref_num():
    """Generates unique reference number for customer enquiries (e.g., ENQ-1001)"""
    last_enquiry = Enquiry.query.order_by(Enquiry.id.desc()).first()
    if last_enquiry and last_enquiry.id:
        next_id = last_enquiry.id + 1001
    else:
        next_id = 1001
    return f"ENQ-{next_id}"

def seed_default_data():
    """Seeds initial database with admin user and sample enquiries & leads if empty."""
    if Admin.query.count() == 0:
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)

    if Enquiry.query.count() == 0:
        eq1 = Enquiry(
            ref_num='ENQ-1001',
            customer_name='John Doe',
            phone_number='9876543210',
            email='john@example.com',
            subject='Web Development Services',
            message='Looking for a custom business website for our retail shop.',
            enquiry_date=date.today(),
            status='New'
        )
        eq2 = Enquiry(
            ref_num='ENQ-1002',
            customer_name='Sarah Smith',
            phone_number='9876543211',
            email='sarah@techcorp.com',
            subject='SEO & Marketing Package',
            message='Need consultation regarding digital marketing and lead generation.',
            enquiry_date=date.today(),
            status='In Progress',
            admin_response='Scheduled initial discussion call for tomorrow.'
        )
        eq3 = Enquiry(
            ref_num='ENQ-1003',
            customer_name='Michael Brown',
            phone_number='9876543212',
            email='michael@designstudio.com',
            subject='Software Maintenance',
            message='Inquiring about annual maintenance contract for existing CRM.',
            enquiry_date=date.today(),
            status='Responded',
            admin_response='Sent quotation details via email.'
        )
        db.session.add_all([eq1, eq2, eq3])
        db.session.commit()

        lead1 = Lead(
            enquiry_id=eq1.id,
            customer_name='John Doe',
            phone_number='9876543210',
            email='john@example.com',
            requirement='Custom business website with e-commerce features.',
            status='New Lead',
            follow_up_date=date.today(),
            notes='Customer requested proposal by weekend.'
        )
        lead2 = Lead(
            enquiry_id=eq2.id,
            customer_name='Sarah Smith',
            phone_number='9876543211',
            email='sarah@techcorp.com',
            requirement='Full digital marketing setup and SEO audit.',
            status='Follow-up',
            follow_up_date=date.today(),
            notes='Follow up regarding budget approval.'
        )
        db.session.add_all([lead1, lead2])
        db.session.commit()

        f1 = FollowUp(
            lead_id=lead2.id,
            follow_up_date=date.today(),
            notes='Called Sarah to review proposal draft.',
            status_at_time='Follow-up'
        )
        db.session.add(f1)
        db.session.commit()

# Admin Auth Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as Administrator to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# PUBLIC CUSTOMER ROUTES

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enquiry', methods=['GET', 'POST'])
def enquiry():
    if request.method == 'POST':
        customer_name = request.form.get('customer_name', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        email = request.form.get('email', '').strip().lower()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        enquiry_date_str = request.form.get('enquiry_date', '').strip()

        if not customer_name or not phone_number or not email or not subject or not message:
            flash('All required fields must be filled out.', 'danger')
            return redirect(url_for('enquiry'))

        try:
            enquiry_date_val = datetime.strptime(enquiry_date_str, '%Y-%m-%d').date() if enquiry_date_str else date.today()
        except ValueError:
            enquiry_date_val = date.today()

        ref_num = generate_ref_num()

        new_enquiry = Enquiry(
            ref_num=ref_num,
            customer_name=customer_name,
            phone_number=phone_number,
            email=email,
            subject=subject,
            message=message,
            enquiry_date=enquiry_date_val,
            status='New'
        )
        db.session.add(new_enquiry)
        db.session.commit()

        return redirect(url_for('enquiry_success', ref_num=ref_num))

    today_str = date.today().isoformat()
    return render_template('enquiry.html', today=today_str)

@app.route('/enquiry/success/<ref_num>')
def enquiry_success(ref_num):
    enquiry_obj = Enquiry.query.filter_by(ref_num=ref_num).first_or_404()
    return render_template('enquiry_success.html', enquiry=enquiry_obj)

# ADMIN AUTHENTICATION ROUTES

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return redirect(url_for('admin_login'))

        # Check DB first or fallback to env/hardcoded admin
        admin_user = Admin.query.filter_by(username=username).first()
        authenticated = False

        if admin_user and admin_user.check_password(password):
            authenticated = True
        elif username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            authenticated = True

        if authenticated:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Logged in successfully as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin username or password.', 'danger')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ADMIN DASHBOARD & MANAGEMENT ROUTES

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    total_enquiries = Enquiry.query.count()
    new_enquiries = Enquiry.query.filter_by(status='New').count()
    in_progress_enquiries = Enquiry.query.filter_by(status='In Progress').count()
    responded_enquiries = Enquiry.query.filter_by(status='Responded').count()
    closed_enquiries = Enquiry.query.filter_by(status='Closed').count()

    total_leads = Lead.query.count()
    followup_leads = Lead.query.filter_by(status='Follow-up').count()
    converted_leads = Lead.query.filter_by(status='Converted').count()

    recent_enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).limit(5).all()
    upcoming_followups = Lead.query.filter(Lead.follow_up_date.isnot(None)).order_by(Lead.follow_up_date.asc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_enquiries=total_enquiries,
        new_enquiries=new_enquiries,
        in_progress_enquiries=in_progress_enquiries,
        responded_enquiries=responded_enquiries,
        closed_enquiries=closed_enquiries,
        total_leads=total_leads,
        followup_leads=followup_leads,
        converted_leads=converted_leads,
        recent_enquiries=recent_enquiries,
        upcoming_followups=upcoming_followups
    )

@app.route('/admin/enquiries')
@admin_required
def enquiries():
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Enquiry.query

    if search_query:
        query = query.filter(
            (Enquiry.customer_name.ilike(f'%{search_query}%')) |
            (Enquiry.email.ilike(f'%{search_query}%')) |
            (Enquiry.phone_number.ilike(f'%{search_query}%')) |
            (Enquiry.subject.ilike(f'%{search_query}%')) |
            (Enquiry.ref_num.ilike(f'%{search_query}%'))
        )

    if status_filter:
        query = query.filter(Enquiry.status == status_filter)

    all_enquiries = query.order_by(Enquiry.created_at.desc()).all()
    return render_template('enquiries.html', enquiries=all_enquiries, q=search_query, selected_status=status_filter)

@app.route('/admin/enquiry/<int:id>')
@admin_required
def enquiry_details(id):
    enquiry_obj = Enquiry.query.get_or_404(id)
    return render_template('enquiry_details.html', enquiry=enquiry_obj)

@app.route('/admin/enquiry/<int:id>/update', methods=['POST'])
@admin_required
def update_enquiry(id):
    enquiry_obj = Enquiry.query.get_or_404(id)
    status = request.form.get('status', enquiry_obj.status)
    admin_response = request.form.get('admin_response', '').strip()

    enquiry_obj.status = status
    if admin_response:
        enquiry_obj.admin_response = admin_response

    db.session.commit()
    flash(f'Enquiry #{enquiry_obj.ref_num} updated successfully.', 'success')
    return redirect(url_for('enquiry_details', id=id))

@app.route('/admin/enquiry/<int:id>/convert', methods=['POST'])
@admin_required
def convert_to_lead(id):
    enquiry_obj = Enquiry.query.get_or_404(id)
    requirement = request.form.get('requirement', '').strip() or f"Enquiry Subject: {enquiry_obj.subject}\nDetails: {enquiry_obj.message}"
    notes = request.form.get('notes', '').strip() or "Converted from online customer enquiry."
    follow_up_date_str = request.form.get('follow_up_date', '').strip()

    follow_up_date_val = None
    if follow_up_date_str:
        try:
            follow_up_date_val = datetime.strptime(follow_up_date_str, '%Y-%m-%d').date()
        except ValueError:
            follow_up_date_val = date.today()

    new_lead = Lead(
        enquiry_id=enquiry_obj.id,
        customer_name=enquiry_obj.customer_name,
        phone_number=enquiry_obj.phone_number,
        email=enquiry_obj.email,
        requirement=requirement,
        status='New Lead',
        follow_up_date=follow_up_date_val,
        notes=notes
    )
    enquiry_obj.status = 'In Progress'

    db.session.add(new_lead)
    db.session.commit()

    flash(f'Enquiry #{enquiry_obj.ref_num} converted to Lead successfully.', 'success')
    return redirect(url_for('lead_details', id=new_lead.id))

@app.route('/admin/enquiry/<int:id>/delete', methods=['POST'])
@admin_required
def delete_enquiry(id):
    enquiry_obj = Enquiry.query.get_or_404(id)
    ref = enquiry_obj.ref_num
    db.session.delete(enquiry_obj)
    db.session.commit()
    flash(f'Enquiry {ref} deleted successfully.', 'info')
    return redirect(url_for('enquiries'))

@app.route('/admin/leads')
@admin_required
def leads():
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Lead.query

    if search_query:
        query = query.filter(
            (Lead.customer_name.ilike(f'%{search_query}%')) |
            (Lead.email.ilike(f'%{search_query}%')) |
            (Lead.phone_number.ilike(f'%{search_query}%')) |
            (Lead.requirement.ilike(f'%{search_query}%'))
        )

    if status_filter:
        query = query.filter(Lead.status == status_filter)

    all_leads = query.order_by(Lead.created_at.desc()).all()
    return render_template('leads.html', leads=all_leads, q=search_query, selected_status=status_filter)

@app.route('/admin/lead/<int:id>')
@admin_required
def lead_details(id):
    lead_obj = Lead.query.get_or_404(id)
    followups = FollowUp.query.filter_by(lead_id=id).order_by(FollowUp.created_at.desc()).all()
    today_str = date.today().isoformat()
    return render_template('lead_details.html', lead=lead_obj, followups=followups, today=today_str)

@app.route('/admin/lead/<int:id>/update', methods=['POST'])
@admin_required
def update_lead(id):
    lead_obj = Lead.query.get_or_404(id)
    status = request.form.get('status', lead_obj.status)
    requirement = request.form.get('requirement', lead_obj.requirement).strip()
    notes = request.form.get('notes', '').strip()
    follow_up_date_str = request.form.get('follow_up_date', '').strip()

    lead_obj.status = status
    lead_obj.requirement = requirement

    if notes:
        lead_obj.notes = notes

    if follow_up_date_str:
        try:
            lead_obj.follow_up_date = datetime.strptime(follow_up_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # If new notes or follow-up date was set, create a FollowUp history record
    if notes or follow_up_date_str:
        f_date = lead_obj.follow_up_date or date.today()
        f_notes = notes if notes else "Status or follow-up date updated."
        followup_record = FollowUp(
            lead_id=lead_obj.id,
            follow_up_date=f_date,
            notes=f_notes,
            status_at_time=status
        )
        db.session.add(followup_record)

    db.session.commit()
    flash(f'Lead details for {lead_obj.customer_name} updated.', 'success')
    return redirect(url_for('lead_details', id=id))

@app.route('/admin/lead/<int:id>/delete', methods=['POST'])
@admin_required
def delete_lead(id):
    lead_obj = Lead.query.get_or_404(id)
    name = lead_obj.customer_name
    db.session.delete(lead_obj)
    db.session.commit()
    flash(f'Lead for {name} deleted successfully.', 'info')
    return redirect(url_for('leads'))

@app.route('/admin/followups')
@admin_required
def followups():
    all_leads = Lead.query.order_by(Lead.customer_name.asc()).all()
    all_followups = FollowUp.query.order_by(FollowUp.created_at.desc()).all()
    upcoming_leads = Lead.query.filter(Lead.follow_up_date.isnot(None)).order_by(Lead.follow_up_date.asc()).all()
    today_str = date.today().isoformat()
    return render_template('followups.html', leads=all_leads, followups=all_followups, upcoming_leads=upcoming_leads, today=today_str)

@app.route('/admin/followup/add', methods=['POST'])
@admin_required
def add_followup():
    lead_id = request.form.get('lead_id', type=int)
    follow_up_date_str = request.form.get('follow_up_date', '').strip()
    notes = request.form.get('notes', '').strip()
    status = request.form.get('status', '').strip()

    if not lead_id or not follow_up_date_str or not notes:
        flash('Please select a lead, follow-up date, and enter notes.', 'danger')
        return redirect(url_for('followups'))

    lead_obj = Lead.query.get_or_404(lead_id)

    try:
        f_date = datetime.strptime(follow_up_date_str, '%Y-%m-%d').date()
    except ValueError:
        f_date = date.today()

    if status:
        lead_obj.status = status

    lead_obj.follow_up_date = f_date
    lead_obj.notes = notes

    new_followup = FollowUp(
        lead_id=lead_obj.id,
        follow_up_date=f_date,
        notes=notes,
        status_at_time=lead_obj.status
    )

    db.session.add(new_followup)
    db.session.commit()

    flash(f'Follow-up added for {lead_obj.customer_name}.', 'success')
    return redirect(url_for('followups'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_default_data()
    app.run(debug=True)
