from app import create_app, db
from models import User, Customer, Loan, Payment, Expenditure, Master

app = create_app()

with app.app_context():
    print("SQLALCHEMY_DATABASE_URI =", app.config.get("SQLALCHEMY_DATABASE_URI"))
    db.create_all()
    print("✅ Database initialized: all tables created.")
