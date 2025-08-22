# Parking Management System

## Overview

This is a web-based Parking Management System built with Flask. It allows users to book parking spots, manage bookings, and provides an admin dashboard for managing parking lots, users, and records. The system supports user authentication, role-based access (admin/user), and payment summary generation.

## Features

- User registration and login
- Admin and user dashboards
- Add, edit, and manage parking lots (admin)
- Book and release parking spots (user)
- View booking history and payment summary
- QR code generation for payments
- Search and filter parking lots
- Profile management for users and admin
- Secure password storage and authentication

## Tech Stack

- Python 3
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite (default, can be changed)
- Jinja2 (templating)
- QRCode (for payment QR generation)

## Project Structure

```
app.py                  # Main application entry point
requirements.txt        # Python dependencies
controllers/            # Flask Blueprints for auth, user, admin
models/                 # SQLAlchemy models
static/                 # Static files (images, CSS, JS)
templates/              # HTML templates (Jinja2)
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repo-url>
   cd Parking-Management-System
   ```
2. **Create a virtual environment (optional but recommended):**
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```
   python app.py
   ```
5. **Access the app:**
   Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Default Admin Login

- Username: `admin`
- Password: `admin`

## Screenshots

Add screenshots of the dashboard, booking, and admin pages here.

## License

This project is for educational purposes.
