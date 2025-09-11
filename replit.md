# Daily Loan Collection System

## Overview

A comprehensive loan management system designed for daily loan collection operations. The application provides complete customer management, automated loan interest calculations, payment tracking, and expenditure management. It features a web-based interface with Progressive Web App (PWA) capabilities for mobile access, making it suitable for field operations and office management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **PWA Implementation**: Service worker, manifest.json, and offline capabilities for mobile field work
- **CSS Framework**: Bootstrap 5 with custom CSS for loan management specific styling
- **JavaScript**: Vanilla JavaScript with automatic form validation and loan calculation features

### Backend Architecture
- **Web Framework**: Flask with modular route organization
- **Database ORM**: SQLAlchemy with declarative base model structure
- **Authentication**: Integrated Replit Auth system with OAuth2 flow
- **Session Management**: Flask-Login with persistent sessions (7-day lifetime)
- **Security**: CSRF protection via Flask-WTF, secure file uploads with 16MB limit
- **Configuration**: Environment-based config with development/production profiles

### Data Storage Architecture
- **Primary Database**: PostgreSQL (configured via DATABASE_URL environment variable)
- **Connection Pooling**: SQLAlchemy engine with pre-ping and 300-second recycle
- **File Storage**: Local filesystem for customer documents and photos in uploads/ directory
- **Session Storage**: Database-backed OAuth token storage linked to browser sessions

### Core Business Logic
- **Loan Management**: Support for daily, weekly, and monthly loan periods with configurable interest rates
- **Interest Calculations**: Precise decimal calculations with per-hundred rate system
- **Payment Tracking**: Complete payment history with loan balance calculations
- **Customer Organization**: Hierarchical structure with Areas > Lines > Customers
- **Expenditure Management**: Business expense tracking with categorization

### Authentication & Authorization
- **Replit Auth Integration**: Mandatory User and OAuth tables for seamless authentication
- **User Management**: Profile information storage with email, name, and profile images
- **Session Security**: Browser-specific session keys tied to OAuth tokens
- **Access Control**: Login requirements on all protected routes with automatic redirects

## External Dependencies

### Third-Party Services
- **Replit Auth**: Primary authentication provider with OAuth2 flow
- **CDN Resources**: Bootstrap 5 CSS/JS and Bootstrap Icons from jsDelivr CDN

### Database Requirements
- **PostgreSQL**: Primary data storage (configurable via DATABASE_URL)
- **SQLAlchemy**: ORM with automatic table creation and migration support

### Frontend Libraries
- **Bootstrap 5**: UI framework for responsive design
- **Bootstrap Icons**: Icon library for consistent visual elements
- **Service Worker**: Browser API for offline functionality and caching

### File System Dependencies
- **Upload Directory**: Local filesystem storage for customer documents
- **Static Assets**: CSS, JavaScript, and PWA manifest files
- **Template System**: Jinja2 template inheritance for consistent UI

### Environment Variables
- **SESSION_SECRET**: Flask session encryption key
- **DATABASE_URL**: PostgreSQL connection string
- **Upload Configuration**: File size limits and allowed extensions