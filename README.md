# Daily Loan Collection System

A comprehensive loan management system designed for daily loan collection operations with Progressive Web App (PWA) capabilities for mobile access.

## Features

### Core Functionality
- **Customer Management**: Add customers with document uploads and organize by areas/lines
- **Loan Management**: Create loans with automatic interest calculations (daily/weekly/monthly)
- **Payment Tracking**: Record payments and track loan progress
- **Expenditure Management**: Track business expenses and categorization
- **Master Data**: Manage areas, lines, and configurable interest rates

### Mobile App Features
- **Progressive Web App (PWA)**: Install on mobile devices like a native app
- **Offline Functionality**: Core features work without internet connection
- **Touch-Optimized Interface**: Designed for mobile touchscreens
- **Responsive Design**: Works on phones, tablets, and desktops

### Security Features
- **Replit Auth Integration**: Secure OAuth2 authentication
- **CSRF Protection**: Protected against cross-site request forgery
- **Session Management**: Secure 7-day persistent sessions
- **File Upload Security**: Validated file uploads with size limits

## Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- Web server with HTTPS (required for PWA features)

### Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file or set the following environment variables:
   ```
   SESSION_SECRET=your-secret-key-here
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ```

3. **Database Setup**
   The application will automatically create database tables on first run.

4. **Run the Application**
   ```bash
   python main.py
   ```

5. **Access the Application**
   - Open browser to `http://localhost:5000`
   - For PWA features, access via HTTPS in production

## Project Structure

```
daily-loan-collection/
├── app.py                 # Flask application initialization
├── main.py               # Application entry point
├── routes.py             # All route definitions
├── models.py             # Database models
├── config.py             # Configuration settings
├── replit_auth.py        # Authentication integration
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── layout.html       # Base template
│   ├── dashboard.html    # Dashboard page
│   ├── customers/        # Customer templates
│   ├── loans/            # Loan templates
│   ├── payments/         # Payment templates
│   ├── expenditures/     # Expenditure templates
│   └── master/           # Master data templates
├── static/               # Static files
│   ├── css/
│   │   └── layout.css    # Main stylesheet
│   ├── js/
│   │   └── app.js        # JavaScript functionality
│   ├── icons/            # PWA app icons
│   ├── manifest.json     # PWA manifest
│   └── sw.js             # Service worker
└── uploads/              # User uploaded files (created automatically)
```

## Usage

### Initial Setup
1. **Create Areas**: Define geographical or organizational areas
2. **Add Lines**: Create lines within areas for customer organization
3. **Set Interest Rates**: Configure rates for daily, weekly, and monthly periods

### Daily Operations
1. **Add Customers**: Register customers with personal details and documents
2. **Create Loans**: Issue loans with automatic interest calculations
3. **Record Payments**: Track daily payments and loan progress
4. **Manage Expenses**: Record business expenditures

### Mobile App Usage
1. **Install PWA**: Visit the app in a mobile browser and tap "Install"
2. **Use Offline**: Core features work without internet connection
3. **Field Operations**: Perfect for loan officers working in the field

## Technical Details

### Database Schema
- **Users**: Authentication and user management
- **Areas/Lines**: Hierarchical customer organization
- **Customers**: Customer details with document storage
- **Interest Rates**: Configurable rates by period
- **Loans**: Loan records with calculated amounts
- **Payments**: Payment history and tracking
- **Expenditures**: Business expense tracking

### Interest Calculation
- **Per Hundred System**: Interest calculated per ₹100 of loan amount
- **Period-based**: Different rates for daily, weekly, monthly
- **Automatic Calculation**: Total interest and payment amounts computed automatically

### PWA Features
- **Service Worker**: Caches essential files for offline use
- **App Manifest**: Defines app appearance and behavior
- **Mobile Optimization**: Touch-friendly interface design
- **Install Prompt**: Browser-native installation prompts

## Deployment

### Production Deployment
1. **Database**: Set up PostgreSQL database
2. **HTTPS**: Configure SSL certificate (required for PWA)
3. **Environment**: Set production environment variables
4. **WSGI Server**: Use Gunicorn or similar for production
5. **Static Files**: Serve static files with proper caching headers

### Example Production Command
```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 main:app
```

## Support

For technical support or questions about implementation, refer to the Flask documentation and the specific libraries used in this project.

## License

This project is provided as-is for educational and business use.