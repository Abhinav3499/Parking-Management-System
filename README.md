# Vehicle Parking Management System

A Flask-based web application for managing vehicle parking with separate admin and user interfaces.

## Features

### Admin Features
- **Dashboard**: Overview of all users and parking lots
- **Add Location**: Create new parking locations with address and pin code
- **Add Parking Lot**: Create parking lots at specific locations with total spots and pricing
- **View Parking Lots**: See all parking lots organized by location
- **User Management**: View all registered users

### User Features
- **Dashboard**: Personal dashboard with recent booking history
- **Book Parking**: Two-step booking process:
  1. Select location
  2. Choose from available parking lots with real-time spot availability
- **View History**: Complete parking history with entry/exit times
- **View Summary**: Statistics including total bookings, active bookings, and most visited location
- **Exit Parking**: Release parking spots when leaving

## Technical Features
- **Real-time Spot Tracking**: Shows available spots for each parking lot
- **Session Management**: Secure login/logout with session tracking
- **Responsive Design**: Clean, modern UI with consistent styling
- **Navigation**: Back buttons and logout buttons on all pages
- **Data Validation**: Proper form validation and error handling

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install flask flask-sqlalchemy werkzeug
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the Application**:
   - Open browser and go to `http://localhost:5000`
   - Admin login: username: `admin`, password: `admin`
   - Register new users for testing

## Database Schema

- **User**: username, password, name, admin flag
- **Location**: name, address, pin code
- **ParkingLot**: location_id, total_spots, price
- **ParkingStatus**: tracks filled spots for each lot
- **ParkingRecord**: user bookings with entry/exit times

## File Structure

```
/parking_app
├── app.py              # Main Flask application
├── models.py           # Database models
├── static/
│   └── style.css       # Styling for all pages
├── templates/          # HTML templates
│   ├── index.html      # Login page
│   ├── register.html   # User registration
│   ├── userDashboard.html
│   ├── adminDashboard.html
│   ├── book.html       # Booking interface
│   ├── history.html    # Parking history
│   ├── summary.html    # User statistics
│   ├── addLocation.html
│   ├── addParkingLot.html
│   └── viewParkingLots.html
└── parking.db          # SQLite database (created automatically)
```

## Recent Updates

- ✅ Added logout button to all pages
- ✅ Added back button to all pages (except main login)
- ✅ Improved booking flow: location selection → parking lot selection
- ✅ Real-time spot availability display
- ✅ Enhanced UI with consistent styling
- ✅ Added user summary page with statistics
- ✅ Improved error handling and validation