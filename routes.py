import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from flask import render_template, request, flash, redirect, url_for, session, current_app, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import and_, or_

from app import app, db
from replit_auth import make_replit_blueprint, require_login
from models import (
    User, Area, Line, InterestRate, Customer, Loan, Payment, 
    Expenditure, LoanPeriod
)

# Register the Replit Auth blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

# Utility functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def calculate_loan_details(loan_amount, period, duration_days, interest_rate):
    """Calculate loan interest and payment amounts"""
    loan_amount = Decimal(str(loan_amount))
    interest_rate = Decimal(str(interest_rate))
    duration_days = int(duration_days)
    
    # Calculate total interest based on period
    if period == LoanPeriod.DAILY:
        # Daily interest calculation
        total_interest = (loan_amount * interest_rate * duration_days) / Decimal('100')
        total_amount = loan_amount + total_interest
        daily_amount = total_amount / duration_days
        return {
            'total_interest': total_interest,
            'total_amount': total_amount,
            'daily_amount': daily_amount,
            'weekly_amount': None,
            'monthly_amount': None
        }
    elif period == LoanPeriod.WEEKLY:
        # Weekly interest calculation
        weeks = duration_days / 7
        total_interest = (loan_amount * interest_rate * weeks) / Decimal('100')
        total_amount = loan_amount + total_interest
        weekly_amount = total_amount / Decimal(str(weeks))
        return {
            'total_interest': total_interest,
            'total_amount': total_amount,
            'daily_amount': None,
            'weekly_amount': weekly_amount,
            'monthly_amount': None
        }
    elif period == LoanPeriod.MONTHLY:
        # Monthly interest calculation
        months = duration_days / 30
        total_interest = (loan_amount * interest_rate * months) / Decimal('100')
        total_amount = loan_amount + total_interest
        monthly_amount = total_amount / Decimal(str(months))
        return {
            'total_interest': total_interest,
            'total_amount': total_amount,
            'daily_amount': None,
            'weekly_amount': None,
            'monthly_amount': monthly_amount
        }

# Routes
@app.route('/')
def index():
    """Landing page - show login button for anonymous users, dashboard for authenticated users"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard for authenticated users"""
    # Get some basic statistics
    total_customers = Customer.query.filter_by(is_active=True).count()
    active_loans = Loan.query.filter_by(is_active=True, is_paid=False).count()
    total_loan_amount = db.session.query(db.func.sum(Loan.loan_amount)).filter(
        Loan.is_active == True, Loan.is_paid == False
    ).scalar() or 0
    
    # Recent loans
    recent_loans = Loan.query.filter_by(is_active=True).order_by(
        Loan.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_customers=total_customers,
                         active_loans=active_loans,
                         total_loan_amount=total_loan_amount,
                         recent_loans=recent_loans)

# Master Forms Routes
@app.route('/master/areas')
@require_login
def areas():
    """Area management page"""
    areas_list = Area.query.filter_by(is_active=True).all()
    return render_template('master/areas.html', areas=areas_list)

@app.route('/master/areas/add', methods=['GET', 'POST'])
@require_login
def add_area():
    """Add new area"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Area name is required', 'error')
            return render_template('master/add_area.html')
        
        # Check for duplicate
        existing = Area.query.filter_by(name=name, is_active=True).first()
        if existing:
            flash('Area name already exists', 'error')
            return render_template('master/add_area.html')
        
        area = Area(
            name=name,
            description=description,
            created_by=current_user.id
        )
        db.session.add(area)
        db.session.commit()
        
        flash('Area added successfully', 'success')
        return redirect(url_for('areas'))
    
    return render_template('master/add_area.html')

@app.route('/master/lines')
@require_login
def lines():
    """Line management page"""
    lines_list = Line.query.filter_by(is_active=True).all()
    return render_template('master/lines.html', lines=lines_list)

@app.route('/master/lines/add', methods=['GET', 'POST'])
@require_login
def add_line():
    """Add new line"""
    if request.method == 'POST':
        name = request.form.get('name')
        area_id = request.form.get('area_id')
        description = request.form.get('description')
        
        if not name or not area_id:
            flash('Line name and area are required', 'error')
            return redirect(url_for('add_line'))
        
        line = Line(
            name=name,
            area_id=area_id,
            description=description,
            created_by=current_user.id
        )
        db.session.add(line)
        db.session.commit()
        
        flash('Line added successfully', 'success')
        return redirect(url_for('lines'))
    
    areas_list = Area.query.filter_by(is_active=True).all()
    return render_template('master/add_line.html', areas=areas_list)

@app.route('/master/interest-rates')
@require_login
def interest_rates():
    """Interest rate management page"""
    rates = InterestRate.query.filter_by(is_active=True).all()
    return render_template('master/interest_rates.html', rates=rates)

@app.route('/master/interest-rates/add', methods=['GET', 'POST'])
@require_login
def add_interest_rate():
    """Add new interest rate"""
    if request.method == 'POST':
        period = request.form.get('period')
        rate_per_hundred = request.form.get('rate_per_hundred')
        
        if not period or not rate_per_hundred:
            flash('Period and interest rate are required', 'error')
            return render_template('master/add_interest_rate.html')
        
        # Check for existing rate for this period
        existing = InterestRate.query.filter_by(
            period=LoanPeriod(period), is_active=True
        ).first()
        if existing:
            flash('Interest rate for this period already exists', 'error')
            return render_template('master/add_interest_rate.html')
        
        rate = InterestRate(
            period=LoanPeriod(period),
            rate_per_hundred=Decimal(rate_per_hundred),
            created_by=current_user.id
        )
        db.session.add(rate)
        db.session.commit()
        
        flash('Interest rate added successfully', 'success')
        return redirect(url_for('interest_rates'))
    
    return render_template('master/add_interest_rate.html')

# Customer Management Routes
@app.route('/customers')
@require_login
def customers():
    """Customer list page"""
    customers_list = Customer.query.filter_by(is_active=True).all()
    return render_template('customers/list.html', customers=customers_list)

@app.route('/customers/add', methods=['GET', 'POST'])
@require_login
def add_customer():
    """Add new customer"""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        line_id = request.form.get('line_id')
        
        if not name or not line_id:
            flash('Customer name and line are required', 'error')
            return redirect(url_for('add_customer'))
        
        # Handle file upload
        document_path = None
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(current_app.root_path, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                # Save file with timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                document_path = filename
        
        customer = Customer(
            name=name,
            phone=phone,
            address=address,
            line_id=line_id,
            document_path=document_path,
            created_by=current_user.id
        )
        db.session.add(customer)
        db.session.commit()
        
        flash('Customer added successfully', 'success')
        return redirect(url_for('customers'))
    
    lines_list = Line.query.filter_by(is_active=True).all()
    return render_template('customers/add.html', lines=lines_list)

# Loan Management Routes
@app.route('/loans')
@require_login
def loans():
    """Loan list page"""
    loans_list = Loan.query.filter_by(is_active=True).order_by(Loan.created_at.desc()).all()
    return render_template('loans/list.html', loans=loans_list)

@app.route('/loans/add', methods=['GET', 'POST'])
@require_login
def add_loan():
    """Add new loan"""
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        loan_amount = request.form.get('loan_amount')
        period = request.form.get('period')
        duration_days = request.form.get('duration_days')
        interest_rate = request.form.get('interest_rate')
        start_date_str = request.form.get('start_date')
        
        if not all([customer_id, loan_amount, period, duration_days, interest_rate, start_date_str]):
            flash('All fields are required', 'error')
            return redirect(url_for('add_loan'))
        
        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = start_date + timedelta(days=int(duration_days))
        
        # Calculate loan details
        loan_details = calculate_loan_details(
            loan_amount, LoanPeriod(period), duration_days, interest_rate
        )
        
        loan = Loan(
            customer_id=customer_id,
            loan_amount=Decimal(loan_amount),
            period=LoanPeriod(period),
            duration_days=int(duration_days),
            interest_rate=Decimal(interest_rate),
            total_interest=loan_details['total_interest'],
            total_amount=loan_details['total_amount'],
            daily_amount=loan_details['daily_amount'],
            weekly_amount=loan_details['weekly_amount'],
            monthly_amount=loan_details['monthly_amount'],
            start_date=start_date,
            end_date=end_date,
            created_by=current_user.id
        )
        
        db.session.add(loan)
        db.session.commit()
        
        flash('Loan added successfully', 'success')
        return redirect(url_for('loans'))
    
    customers_list = Customer.query.filter_by(is_active=True).all()
    interest_rates = InterestRate.query.filter_by(is_active=True).all()
    return render_template('loans/add.html', customers=customers_list, interest_rates=interest_rates)

# Payment Routes
@app.route('/payments')
@require_login
def payments():
    """Payment history page"""
    payments_list = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('payments/list.html', payments=payments_list)

@app.route('/payments/add/<int:loan_id>', methods=['GET', 'POST'])
@require_login
def add_payment(loan_id):
    """Add payment for a specific loan"""
    loan = Loan.query.get_or_404(loan_id)
    
    if request.method == 'POST':
        amount_paid = request.form.get('amount_paid')
        payment_date_str = request.form.get('payment_date')
        notes = request.form.get('notes')
        
        if not amount_paid or not payment_date_str:
            flash('Amount and payment date are required', 'error')
            return redirect(url_for('add_payment', loan_id=loan_id))
        
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        
        payment = Payment(
            loan_id=loan_id,
            amount_paid=Decimal(amount_paid),
            payment_date=payment_date,
            notes=notes,
            created_by=current_user.id
        )
        
        db.session.add(payment)
        
        # Check if loan is fully paid
        total_payments = db.session.query(db.func.sum(Payment.amount_paid)).filter(
            Payment.loan_id == loan_id
        ).scalar() or Decimal('0')
        
        if total_payments + Decimal(amount_paid) >= loan.total_amount:
            loan.is_paid = True
        
        db.session.commit()
        flash('Payment recorded successfully', 'success')
        return redirect(url_for('loans'))
    
    return render_template('payments/add.html', loan=loan)

# Expenditure Routes
@app.route('/expenditures')
@require_login
def expenditures():
    """Expenditure list page"""
    expenditures_list = Expenditure.query.order_by(Expenditure.created_at.desc()).all()
    return render_template('expenditures/list.html', expenditures=expenditures_list)

@app.route('/expenditures/add', methods=['GET', 'POST'])
@require_login
def add_expenditure():
    """Add new expenditure"""
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')
        category = request.form.get('category')
        expenditure_date_str = request.form.get('expenditure_date')
        
        if not description or not amount or not expenditure_date_str:
            flash('Description, amount, and date are required', 'error')
            return render_template('expenditures/add.html')
        
        expenditure_date = datetime.strptime(expenditure_date_str, '%Y-%m-%d').date()
        
        expenditure = Expenditure(
            description=description,
            amount=Decimal(amount),
            category=category,
            expenditure_date=expenditure_date,
            created_by=current_user.id
        )
        
        db.session.add(expenditure)
        db.session.commit()
        
        flash('Expenditure added successfully', 'success')
        return redirect(url_for('expenditures'))
    
    return render_template('expenditures/add.html')

# API endpoints for dynamic data
@app.route('/api/interest-rate/<period>')
@require_login
def get_interest_rate(period):
    """Get interest rate for a specific period"""
    try:
        period_enum = LoanPeriod(period)
        rate = InterestRate.query.filter_by(period=period_enum, is_active=True).first()
        if rate:
            return jsonify({'rate': float(rate.rate_per_hundred)})
        return jsonify({'rate': 10.0})  # Default rate
    except ValueError:
        return jsonify({'rate': 10.0})

from flask_wtf.csrf import exempt

@app.route('/api/calculate-loan', methods=['POST'])
@exempt  # Exempt from CSRF for AJAX calls
@require_login
def calculate_loan():
    """Calculate loan details via API"""
    data = request.get_json()
    loan_amount = data.get('loan_amount')
    period = data.get('period')
    duration_days = data.get('duration_days')
    interest_rate = data.get('interest_rate')
    
    if not all([loan_amount, period, duration_days, interest_rate]):
        return jsonify({'error': 'All fields required'}), 400
    
    try:
        details = calculate_loan_details(
            loan_amount, LoanPeriod(period), duration_days, interest_rate
        )
        # Convert Decimal to float for JSON serialization
        return jsonify({
            'total_interest': float(details['total_interest']),
            'total_amount': float(details['total_amount']),
            'daily_amount': float(details['daily_amount']) if details['daily_amount'] else None,
            'weekly_amount': float(details['weekly_amount']) if details['weekly_amount'] else None,
            'monthly_amount': float(details['monthly_amount']) if details['monthly_amount'] else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400