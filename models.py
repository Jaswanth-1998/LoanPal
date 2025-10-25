# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # optional backrefs
    customers = db.relationship('Customer', backref='owner', lazy=True, cascade='all, delete-orphan')
    loans = db.relationship('Loan', backref='owner', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='owner', lazy=True, cascade='all, delete-orphan')
    expenditures = db.relationship('Expenditure', backref='owner', lazy=True, cascade='all, delete-orphan')
    masters = db.relationship('Master', backref='owner', lazy=True, cascade='all, delete-orphan')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)   # NEW
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)  # remove global unique
    address = db.Column(db.Text)
    area = db.Column(db.String(100))
    line = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    loans = db.relationship('Loan', backref='customer', lazy=True, cascade='all, delete-orphan')

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # NEW
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('Payment', backref='loan', lazy=True, cascade='all, delete-orphan')

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # NEW
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Expenditure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)  # NEW
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expenditure_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Master(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)  # nullable True => global rows ok
    type = db.Column(db.String(50), nullable=False)  # 'area', 'interest_rate', 'line'
    value = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
