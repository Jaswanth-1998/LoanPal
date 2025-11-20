from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import text, func, desc
from app import db
from models import Customer, Loan, Payment, Expenditure, Master
from models import User
from datetime import datetime, date, timedelta
from sqlalchemy import or_, cast
from sqlalchemy.types import String
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask import flash, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

# Profile view/edit
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main.route('/profile/edit', methods=['GET','POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # validate uniqueness of username/email for other users
        username = request.form.get('username')
        email = request.form.get('email')

        # check if username or email taken by other user
        u = User.query.filter(User.id != current_user.id, User.username == username).first()
        if u:
            flash('Username already taken', 'danger')
            return redirect(url_for('main.edit_profile'))

        e = User.query.filter(User.id != current_user.id, User.email == email).first()
        if e:
            flash('Email already in use', 'danger')
            return redirect(url_for('main.edit_profile'))

        current_user.username = username
        current_user.email = email

        db.session.commit()
        flash('Profile updated','success')
        return redirect(url_for('main.profile'))

    return render_template('edit_profile.html')

@main.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    current_pwd = request.form.get('current_password', '')
    new_pwd = request.form.get('new_password', '')
    confirm_pwd = request.form.get('confirm_password', '')

    if not current_pwd or not new_pwd or not confirm_pwd:
        flash('Please fill all password fields', 'danger')
        return redirect(url_for('main.profile'))

    if new_pwd != confirm_pwd:
        flash('New password and confirmation do not match', 'danger')
        return redirect(url_for('main.profile'))

    if not check_password_hash(current_user.password_hash, current_pwd):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('main.profile'))

    current_user.password_hash = generate_password_hash(new_pwd, method='pbkdf2:sha256')
    db.session.commit()
    flash('Password updated successfully', 'success')
    return redirect(url_for('main.profile'))

@main.route('/dashboard')
@login_required
def dashboard():
    uid = current_user.id
    total_customers = db.session.query(Customer).filter_by(user_id=uid).count()
    total_loans = db.session.query(Loan).filter_by(user_id=uid, is_active=True).count()
    total_payments_result = db.session.query(func.sum(Payment.amount)).filter(Payment.user_id == uid).scalar()
    total_payments = total_payments_result or 0.0

    total_expenditures_result = db.session.query(func.sum(Expenditure.amount)).filter(Expenditure.user_id == uid).scalar()
    total_expenditures = total_expenditures_result or 0.0

    return render_template('dashboard.html',
                         total_customers=total_customers,
                         total_loans=total_loans,
                         total_payments=total_payments,
                         total_expenditures=total_expenditures,
                          current_year=datetime.now().year 
                          )

# Customers
@main.route('/customers')
@login_required
def customers():
    # Pagination & search support
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('q', '').strip()

    # Base query: customers that belong to current_user
    query = Customer.query.filter(Customer.user_id == current_user.id).filter(
        or_(Customer.user_id==None, Customer.user_id==current_user.id))
        
     # Apply search (if present)
    if search_query:
        query = query.filter(
            or_(
                Customer.name.ilike(f"%{search_query}%"),
                Customer.phone.ilike(f"%{search_query}%"),
                Customer.area.ilike(f"%{search_query}%"),
                Customer.line.ilike(f"%{search_query}%")
            )
        )

    # paginate and order by name
    pagination = query.order_by(Customer.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    customers_list = pagination.items

    # Render customers/list.html
    return render_template('customers/list.html', customers=customers_list, pagination=pagination, search_query=search_query)

@main.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    # When the form is submitted
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        area = request.form.get('area')
        line = request.form.get('line')

        new_customer = Customer(
            user_id=current_user.id,
            name=name,
            phone=phone,
            address=address,
            area=area,
            line=line
        )

        try:
            db.session.add(new_customer)
            db.session.commit()
            flash("✅ Customer added successfully!", "success")
            return redirect(url_for('main.customers'))
        except IntegrityError as e:
            db.session.rollback()
            if 'customer_phone_key' in str(e.orig):
                flash("⚠️ This phone number already exists. Please use a different one.", "danger")
            else:
                flash("❌ An error occurred while saving. Please try again.", "danger")
            return redirect(url_for('main.add_customer'))

    # When user just visits the Add Customer page
    areas = Master.query.filter(Master.type == 'area').filter(or_(Master.user_id == None, Master.user_id == current_user.id)).all()
    lines = Master.query.filter(Master.type == 'line').filter(or_(Master.user_id == None, Master.user_id == current_user.id)).all()

    return render_template('customers/add.html', areas=areas, lines=lines)

# Loans
@main.route('/loans')
@login_required
def loans():
    page = request.args.get('page', 1, type=int) # ✅ get current page number
    per_page = 10  # ✅ number of records per page                         
    search_query = request.args.get('q', '').strip() # ✅ get search keyword

    # Base query: join Loan -> Customer (so we can search by Customer.name)
    query = Loan.query.join(Customer, Loan.customer_id == Customer.id).filter(
        or_(Loan.user_id == None, Loan.user_id == current_user.id))    
    
    # Apply search filter (customer name or numeric matches on amounts)
    if search_query:
        # if you want to search amounts too, keep the cast parts; otherwise remove them
        query = query.filter(
            or_(
                Customer.name.ilike(f"%{search_query}%"),
                cast(Loan.principal_amount, String).ilike(f"%{search_query}%"),
                cast(Loan.total_amount, String).ilike(f"%{search_query}%")
            )
        )
    
    # Apply Pagination and ordering
    pagination = query.order_by(Loan.id.asc()).paginate(page=page, per_page=per_page, error_out=False )
    
    # Render page/ # ✅ matches Jinja variable
    return render_template('loans/list.html', loans=pagination.items, pagination=pagination, search_query=search_query)

@main.route('/loans/add', methods=['GET', 'POST'])
@login_required
def add_loan():
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        principal_amount = float(request.form.get('principal_amount'))
        interest_rate = float(request.form.get('interest_rate'))
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')

        # ensure customer belongs to current user
        customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first()
        if not customer:
            flash('Customer not found or permission denied', 'danger')
            return redirect(url_for('main.add_loan'))

        total_amount = principal_amount + (principal_amount * interest_rate / 100)

        new_loan = Loan(
            user_id=current_user.id,
            customer_id=customer.id,
            principal_amount=principal_amount,
            interest_rate=interest_rate,
            total_amount=total_amount,
            due_date=due_date
        )
        db.session.add(new_loan)
        db.session.commit()

        flash('Loan added successfully', 'success')
        return redirect(url_for('main.loans'))

    customers = Customer.query.filter_by(user_id=current_user.id).all()
    interest_rates = Master.query.filter(Master.type=='interest_rate').filter(or_(Master.user_id==None, Master.user_id==current_user.id)).all()
    return render_template('loans/add.html', customers=customers, interest_rates=interest_rates)

#PAYMENTS 
@main.route('/payments')
@login_required
def payments():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('q', '').strip()

    # Query active loans for this user
    base_q = Loan.query.join(Customer).filter(
        Loan.user_id == current_user.id,
        Loan.is_active == True
    )

    if search_query:
        base_q = base_q.filter(or_(
            Customer.name.ilike(f"%{search_query}%"),
            cast(Loan.principal_amount, String).ilike(f"%{search_query}%"),
            cast(Loan.total_amount, String).ilike(f"%{search_query}%")
        ))

    pagination = base_q.order_by(Loan.id.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    loans = pagination.items

    # Allowed dates = today + last 3 days
    today_dt = date.today()
    allowed_dates = [(today_dt - timedelta(days=i)).isoformat() for i in range(4)]
    allowed_date_objs = [(today_dt - timedelta(days=i)) for i in range(4)]

    loan_meta = {}

    for loan in loans:
        # paid dates
        paid_rows = (
            db.session.query(func.date(Payment.payment_date))
            .filter(
                Payment.loan_id == loan.id,
                Payment.user_id == current_user.id,
                func.date(Payment.payment_date).in_(allowed_date_objs)
            )
            .distinct()
            .all()
        )
        paid_dates = [p[0].isoformat() for p in paid_rows if p[0] is not None]

        # last payment
        last_row = (
            db.session.query(func.date(Payment.payment_date))
            .filter(
                Payment.loan_id == loan.id,
                Payment.user_id == current_user.id
            )
            .order_by(Payment.payment_date.desc())
            .first()
        )
        last_date = last_row[0].isoformat() if last_row else None

        cust = loan.customer

        loan_meta[loan.id] = {
            "paid_dates": paid_dates,
            "last_payment_date": last_date,
            "customer_area": cust.area if cust else "",
            "customer_line": cust.line if cust else "",
        }

    return render_template(
        "payments/list.html",
        loans=loans,
        pagination=pagination,
        search_query=search_query,
        loan_meta=loan_meta,
        allowed_dates=allowed_dates,
        today=today_dt.isoformat()
    )
    
#ADD PAYMENT 
@main.route('/payments/add', methods=['POST'])
@login_required
def add_payment():
    loan_id = request.form.get("loan_id")
    amount_raw = request.form.get("amount")
    payment_date_raw = request.form.get("payment_date")

    page = request.form.get("page")
    q = request.form.get("q")

    # validate loan
    try:
        loan_id = int(loan_id)
    except:
        flash("Invalid loan", "danger")
        return redirect(url_for("main.payments", page=page, q=q))

    loan = Loan.query.filter_by(id=loan_id, user_id=current_user.id).first()
    if not loan:
        flash("Loan not found", "danger")
        return redirect(url_for("main.payments", page=page, q=q))

    # validate amount
    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError()
    except:
        flash("Enter valid amount", "danger")
        return redirect(url_for("main.payments", page=page, q=q))

    # validate date
    try:
        payment_date = datetime.strptime(payment_date_raw, "%Y-%m-%d")
    except:
        flash("Invalid payment date", "danger")
        return redirect(url_for("main.payments", page=page, q=q))

    # check duplicate
    exist = Payment.query.filter(
        Payment.loan_id == loan.id,
        func.date(Payment.payment_date) == payment_date.date()
    ).first()

    if exist:
        flash("This date already has a payment", "danger")
        return redirect(url_for("main.payments", page=page, q=q))

    # insert payment
    newp = Payment(
        user_id=current_user.id,
        loan_id=loan.id,
        amount=amount,
        payment_date=payment_date
    )
    db.session.add(newp)
    db.session.commit()

    # auto close loan if complete
    total_paid = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0.0)
    ).filter(Payment.loan_id == loan.id).scalar()

    if total_paid >= loan.total_amount:
        loan.is_active = False
        db.session.commit()

    flash("Payment added successfully", "success")
    return redirect(url_for("main.payments", page=page, q=q))

# Expenditures
@main.route('/expenditures')
@login_required
def expenditures():
    page = request.args.get('page', 1, type=int) # ✅ get current page number
    per_page = 10  # ✅ number of records per page                         
    search_query = request.args.get('q', '').strip() # ✅ get search keyword 

    # Base query
    query = Expenditure.query.filter(or_(Expenditure.user_id == None, Expenditure.user_id == current_user.id))

    # Apply search filter (search)
    if search_query:
        query = query.filter(Expenditure.description.ilike(f"%{search_query}%"))

    # Apply Pagination and ordering
    pagination = query.order_by(Expenditure.id.asc()).paginate(page=page, per_page=per_page, error_out=False )

    # Render page/ # ✅ matches Jinja variable
    return render_template( 'expenditures/list.html',expenditures=pagination.items, pagination=pagination, search_query=search_query)

@main.route('/expenditures/add', methods=['GET', 'POST'])
@login_required
def add_expenditure():
    if request.method == 'POST':
        description = request.form.get('description')
        amount = request.form.get('amount')

        new_expenditure = Expenditure(user_id=current_user.id,description=description,amount=float(amount),)
        
        db.session.add(new_expenditure)
        db.session.commit()

        flash('✅ Expenditure added successfully!', 'success')
        return redirect(url_for('main.expenditures'))

    return render_template('expenditures/add.html')

# Master
@main.route('/master')
@login_required
def master():
    page = request.args.get('page', 1, type=int)  # ✅ get current page number
    per_page = 10  # ✅ number of records per page
    search_query = request.args.get('q', '').strip()  # ✅ get search keyword

    # ✅ Base query
    query = Master.query.filter(or_(Master.user_id == None, Master.user_id == current_user.id))

    # ✅ Apply search filter if query present
    if search_query:
        query = query.filter(Master.value.ilike(f'%{search_query}%'))

    # ✅ Apply pagination & Ordering
    pagination = query.order_by(Master.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Render page/ # ✅ matches Jinja variable
    return render_template('master/list.html', master_list=pagination.items, pagination=pagination, search_query=search_query)

@main.route('/master/add', methods=['GET', 'POST'])
@login_required
def add_master():
    if request.method == 'POST':
        mtype = request.form.get('type')
        value = request.form.get('value')

        new_master = Master(user_id=current_user.id, type=mtype, value=value)
        db.session.add(new_master)
        db.session.commit()

        flash('Master data added successfully', 'success')
        return redirect(url_for('main.master'))

    return render_template('master/add.html')

# Reports
@main.route('/reports/users')
@login_required
def user_report():
    """
    Per-customer report for the logged-in user.
    Each row = one customer with customer-specific loan/payment aggregates.
    """
    customers = Customer.query.filter_by(user_id=current_user.id).order_by(Customer.name).all()

    summaries = []
    for c in customers:
        # loans count and sum of principals for this customer
        loan_count = db.session.query(func.count(Loan.id)) \
            .filter(Loan.customer_id == c.id).scalar() or 0

        total_principal = db.session.query(func.coalesce(func.sum(Loan.principal_amount), 0.0)) \
            .filter(Loan.customer_id == c.id).scalar() or 0.0

        # payments: join Payment -> Loan and filter by loan.customer_id
        total_paid = db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)) \
            .join(Loan, Payment.loan_id == Loan.id) \
            .filter(Loan.customer_id == c.id).scalar() or 0.0

        summaries.append({
            'username': current_user.username,
            'customer_name': c.name,
            'loan_count': int(loan_count),
            'total_principal': float(total_principal),
            'total_paid': float(total_paid)
        })

    return render_template('reports/user_report.html', summaries=summaries, is_admin=False)


@main.route('/reports/lines')
@login_required
def line_report():
    """
    Group by Customer.line for current_user and show loan/payment aggregates.
    """
    rows = (
        db.session.query(
            Customer.line.label('line'),
            func.count(Loan.id).label('loan_count'),
            func.coalesce(func.sum(Loan.principal_amount), 0).label('total_principal'),
            func.coalesce(func.sum(Payment.amount), 0).label('total_paid')
        )
        .join(Loan, Loan.customer_id == Customer.id)
        .outerjoin(Payment, Payment.loan_id == Loan.id)
        .filter(Customer.user_id == current_user.id)   # ensure only user's data
        .group_by(Customer.line)
        .order_by(Customer.line)
        .all()
    )
    return render_template('reports/line_report.html', rows=rows)


@main.route('/reports/payments')
@login_required
def payment_report():
    """
    Recent payments for current_user with loan and customer info.
    Optional query param: ?limit=100
    """
    limit = request.args.get('limit', 100, type=int)

    payments = (
        db.session.query(
            Payment.id,
            Payment.amount,
            Payment.payment_date,
            Loan.id.label('loan_id'),
            Customer.name.label('customer_name'),
            Customer.phone.label('customer_phone')
        )
        .join(Loan, Payment.loan_id == Loan.id)
        .join(Customer, Loan.customer_id == Customer.id)
        .filter(Payment.user_id == current_user.id)   # user's payments only
        .order_by(desc(Payment.payment_date))
        .limit(limit)
        .all()
    )
    return render_template('reports/payment_report.html', payments=payments)