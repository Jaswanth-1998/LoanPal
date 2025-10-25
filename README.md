# Daily Loan Collection System

A comprehensive web application for managing daily loan collections, built with Flask and PostgreSQL with Bootstrap UI.

## 🌟 Features

- **Customer Management** - Add and manage customer information
- **Loan Management** - Create and track loans with interest rates
- **Payment Tracking** - Record and monitor loan payments
- **Expenditure Management** - Track business expenses
- **Master Data Management** - Manage areas, interest rates, and lines
- **User Authentication** - Secure login and registration system
- **Bootstrap UI** - Responsive and modern interface
- **PostgreSQL Database** - Robust data storage

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Authentication**: Flask-Login
- **ORM**: Flask-SQLAlchemy

## 📋 Prerequisites

Before running this application, ensure you have the following installed:

- Python 3.8 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- Virtualenv (recommended)

## 🚀 Installation & Setup

### Step 1: Clone or Create Project Structure

```bash
# Create project directory
mkdir daily-loan-collection-system
cd daily-loan-collection-system

# Create the folder structure
mkdir -p templates/customers templates/loans templates/payments templates/expenditures templates/master static/css static/js static/icons uploads
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Database Setup

#### Option A: Using PostgreSQL CLI
```sql
-- Login to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE daily_loans_db;

-- Create user (optional)
CREATE USER loan_user WITH PASSWORD 'loan_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE daily_loans_db TO loan_user;

-- Exit PostgreSQL
\q
```

#### Option B: Using pgAdmin
1. Open pgAdmin
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → Create → Database
4. Name: `daily_loans_db`
5. Click Save

### Step 5: Environment Configuration

Create a `.env` file in the project root:

```env
SESSION_SECRET=your-super-secret-key-change-this-in-production
DATABASE_URL=postgresql://username:password@localhost:5432/daily_loans_db
```

**Example for default PostgreSQL installation:**
```env
SESSION_SECRET=super-secret-key-12345
DATABASE_URL=postgresql://postgres:mypassword123@localhost:5432/daily_loans_db
```

### Step 6: Run the Application

```bash
python main.py
```

The application will start at `http://localhost:5000`

## 📁 Project Structure

```
daily-loan-collection-system/
├── app.py                    # Main Flask application factory
├── main.py                   # Application entry point
├── models.py                 # Database models and relationships
├── routes.py                 # All application routes and logic
├── config.py                 # Configuration settings
├── auth.py                   # Authentication system
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── README.md                # This file
├── .env                     # Environment variables (create this)
├── templates/               # HTML templates
│   ├── customers/           # Customer management pages
│   │   ├── list.html        # Customer listing
│   │   └── add.html         # Add customer form
│   ├── loans/               # Loan management pages
│   │   ├── list.html        # Loan listing
│   │   └── add.html         # Add loan form
│   ├── payments/            # Payment tracking pages
│   │   ├── list.html        # Payment listing
│   │   └── add.html         # Add payment form
│   ├── expenditures/        # Expense management pages
│   │   ├── list.html        # Expenditure listing
│   │   └── add.html         # Add expenditure form
│   ├── master/              # Master data forms
│   │   ├── list.html        # Master data listing
│   │   └── add.html         # Add master data form
│   ├── layout.html          # Base template
│   ├── profile.html         # Profile page
│   ├── edit_profile.html    # Edit user page
│   ├── dashboard.html       # Dashboard page
│   ├── index.html           # Home page
│   ├── login.html           # Login page
│   └── register.html        # Registration page
├── static/                  # Web assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   ├── icons/               # PWA app icons
│   ├── manifest.json        # Mobile app manifest
│   └── sw.js                # Service worker
└── uploads/                 # File upload directory
```

## 🔧 Configuration

### Database Connection
The application uses SQLAlchemy with PostgreSQL. Update the `DATABASE_URL` in your `.env` file:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
```

### Secret Key
Change the `SESSION_SECRET` in production:

```env
SESSION_SECRET=your-very-long-random-secret-key-here
```

## 👤 First Time Setup

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Register a new user:**
   - Navigate to `http://localhost:5000/register`
   - Create your administrator account

3. **Add Master Data:**
   - Go to "Master Data" in the navigation
   - Add your areas (e.g., "Downtown", "Suburbs")
   - Add interest rates (e.g., "5", "10", "15")
   - Add lines if needed

4. **Start Using the System:**
   - Add customers
   - Create loans
   - Record payments and expenditures

## 📊 Database Models

### Users
- System administrators and users
- Authentication and authorization

### Customers
- Customer personal information
- Contact details and area information

### Loans
- Loan principal amount and interest rates
- Start date, due date, and status tracking
- Relationship with customers

### Payments
- Payment amounts and dates
- Linked to specific loans

### Expenditures
- Business expense tracking
- Description and amount

### Master Data
- Areas, interest rates, and lines
- Configurable business parameters

## 🎨 UI Components

### Bootstrap 5 Features Used
- Responsive grid system
- Modern cards and tables
- Form controls and validation
- Navigation bars
- Alert messages
- Badges and buttons
- Icons (Font Awesome)

### Color Scheme
- Primary: Blue (#0d6efd)
- Success: Green (#198754)
- Info: Teal (#0dcaf0)
- Warning: Yellow (#ffc107)
- Danger: Red (#dc3545)

## 🔒 Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection
- Secure database queries with SQLAlchemy
- Environment variable configuration

## 🚀 Deployment Notes

### For Production Deployment

1. **Update Secret Key:**
   ```env
   SESSION_SECRET=very-long-random-string-from-secrets-generator
   ```

2. **Set Debug Mode:**
   ```python
   # In main.py, change to:
   if __name__ == '__main__':
       app.run(debug=False)
   ```

3. **Use Production Database:**
   ```env
   DATABASE_URL=postgresql://username:password@production-server:5432/daily_loans_db
   ```

4. **Consider using:**
   - Gunicorn as WSGI server
   - Nginx as reverse proxy
   - PostgreSQL connection pooling

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Check PostgreSQL is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **Module Not Found Errors:**
   - Verify virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Port Already in Use:**
   ```bash
   # Kill process on port 5000
   sudo lsof -t -i tcp:5000 | xargs kill -9
   ```

4. **Permission Errors:**
   - Ensure proper permissions on uploads directory
   - Check database user privileges

### Debug Mode
For development, you can enable debug mode in `main.py`:
```python
if __name__ == '__main__':
    app.run(debug=True)
```

## 📈 Usage Guide

### Adding a New Customer
1. Navigate to Customers → Add Customer
2. Fill in customer details
3. Select area from master data
4. Submit the form

### Creating a Loan
1. Go to Loans → Add Loan
2. Select existing customer
3. Enter principal amount
4. Choose interest rate from master data
5. Set due date
6. System calculates total amount automatically

### Recording Payments
1. Navigate to Payments → Add Payment
2. Select the loan
3. Enter payment amount
4. Submit to record

### Tracking Expenditures
1. Go to Expenditures → Add Expenditure
2. Enter description and amount
3. Submit to record business expenses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Ensure database connection is working
4. Check application logs for errors

## 🔄 Updates

For future updates:
- Backup your database regularly
- Test updates in a development environment first
- Follow the changelog for breaking changes

---

**Happy Loan Managing! 🎉**

For any questions or issues, please check the troubleshooting section or create an issue in the project repository.