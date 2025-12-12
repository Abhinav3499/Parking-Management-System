# ParkIT - Parking Management System

A modern web app for finding and booking parking spots in Indian cities. Features GPS-based location detection, Google OAuth login, and JWT authentication.

## Features

- **Smart Location Detection** - Find nearby parking lots using GPS
- **Dual Authentication** - Login with password or Google account
- **Real-time Availability** - Check parking spot availability instantly
- **User Dashboard** - View and manage your bookings
- **Admin Panel** - Manage parking lots and monitor bookings
- **QR Code Booking** - Generate QR codes for your reservations

## Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Auth**: JWT tokens, Google OAuth (Authlib)
- **Database**: SQLite (dev), PostgreSQL-ready (production)
- **Frontend**: HTML, CSS (Glassmorphism), Vanilla JavaScript
- **Deployment**: Vercel-ready with WSGI

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abhinav3499/Parking-Management-System.git
   cd Parking-Management-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file:
   ```env
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
   ```

4. **Run the app**
   ```bash
   python app.py
   ```

   Visit http://localhost:5000

### Default Admin Access
- **Username**: `admin`
- **Password**: `admin`

### Project Structure
```
├── app.py                 # Main application
├── config.py              # Configuration
├── controllers/           # Route handlers
├── models/                # Database models
├── utils/                 # JWT & OAuth utilities
├── templates/             # HTML templates
├── static/                # CSS, JS, images
└── instance/              # Database (not in git)
```

### Making Changes

1. **Add a feature** - Create routes in `controllers/`
2. **Update UI** - Edit templates in `templates/`
3. **Modify styles** - Update `static/css/style.css`
4. **Database changes** - Update models in `models/models.py`

## Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URI: `http://localhost:5000/auth/google/callback`
4. Copy Client ID and Secret to `.env`
