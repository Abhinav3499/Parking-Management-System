from app import createApp
from models.models import db, User, Address, ParkingLot, ParkingSpot, ParkingRecord
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with comprehensive Indian parking lot data and test users."""
    
    app = createApp()
    with app.app_context():
        # Create all tables if they don't exist
        print("Creating database tables...")
        db.create_all()
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        try:
            ParkingRecord.query.delete()
            ParkingSpot.query.delete()
            ParkingLot.query.delete()
            User.query.filter_by(isAdmin=False).delete()
            db.session.commit()
        except Exception as e:
            print(f"Note: {e}")
            db.session.rollback()
        
        # Create admin user
        print("Creating admin user...")
        admin_address = Address.query.filter_by(pincode='000000').first()
        if not admin_address:
            admin_address = Address(address='Admin Office, Central Avenue', pincode='000000')
            db.session.add(admin_address)
            db.session.commit()
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                name='Admin',
                addressId=admin_address.id,
                isAdmin=True
            )
            admin_user.setPassword('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("✓ Admin user created (username: admin, password: admin123)")
        
        # Create test users with Indian names
        print("\nCreating test users...")
        test_users_data = [
            {
                'username': 'raj.sharma@email.com',
                'name': 'Raj Sharma',
                'address': 'Flat 301, Green Park Society, Mumbai',
                'pincode': '400001',
                'password': 'user123'
            },
            {
                'username': 'priya.patel@email.com',
                'name': 'Priya Patel',
                'address': 'B-42, Vasant Vihar, Delhi',
                'pincode': '110057',
                'password': 'user123'
            },
            {
                'username': 'arjun.kumar@email.com',
                'name': 'Arjun Kumar',
                'address': '15, MG Road Apartments, Bangalore',
                'pincode': '560001',
                'password': 'user123'
            },
            {
                'username': 'ananya.reddy@email.com',
                'name': 'Ananya Reddy',
                'address': 'Plot 78, Jubilee Hills, Hyderabad',
                'pincode': '500033',
                'password': 'user123'
            }
        ]
        
        test_users = []
        for user_data in test_users_data:
            if not User.query.filter_by(username=user_data['username']).first():
                user_address = Address(
                    address=user_data['address'],
                    pincode=user_data['pincode']
                )
                db.session.add(user_address)
                db.session.commit()
                
                user = User(
                    username=user_data['username'],
                    name=user_data['name'],
                    addressId=user_address.id,
                    isAdmin=False
                )
                user.setPassword(user_data['password'])
                db.session.add(user)
                db.session.commit()
                test_users.append(user)
                print(f"✓ Created user: {user_data['name']} ({user_data['username']})")
        
        # Comprehensive Indian parking lots data
        print("\nCreating parking lots across India...")
        parking_lots_data = [
            # Mumbai (12 locations)
            {'location': 'Bandra West Mall', 'address': 'Linking Road, Bandra West', 'pincode': '400050', 'lat': 19.0596, 'lon': 72.8295, 'price': 80, 'spots': 45},
            {'location': 'Andheri Station Parking', 'address': 'SV Road, Andheri West', 'pincode': '400058', 'lat': 19.1197, 'lon': 72.8464, 'price': 50, 'spots': 35},
            {'location': 'Colaba Causeway', 'address': 'Colaba Causeway', 'pincode': '400005', 'lat': 18.9220, 'lon': 72.8347, 'price': 100, 'spots': 30},
            {'location': 'Powai Business Hub', 'address': 'Hiranandani Gardens, Powai', 'pincode': '400076', 'lat': 19.1176, 'lon': 72.9060, 'price': 70, 'spots': 50},
            {'location': 'Kurla Terminus', 'address': 'LBS Marg, Kurla West', 'pincode': '400070', 'lat': 19.0653, 'lon': 72.8792, 'price': 45, 'spots': 40},
            {'location': 'Dadar Market', 'address': 'Gokhale Road, Dadar', 'pincode': '400028', 'lat': 19.0178, 'lon': 72.8478, 'price': 60, 'spots': 35},
            {'location': 'Juhu Beach Parking', 'address': 'Juhu Tara Road', 'pincode': '400049', 'lat': 19.0990, 'lon': 72.8267, 'price': 70, 'spots': 48},
            {'location': 'BKC Corporate Plaza', 'address': 'Bandra Kurla Complex', 'pincode': '400051', 'lat': 19.0651, 'lon': 72.8694, 'price': 90, 'spots': 42},
            {'location': 'Worli Sea Link Plaza', 'address': 'Worli Seaface', 'pincode': '400018', 'lat': 19.0176, 'lon': 72.8146, 'price': 85, 'spots': 38},
            {'location': 'Goregaon Film City', 'address': 'Film City Road, Goregaon', 'pincode': '400065', 'lat': 19.1542, 'lon': 72.8559, 'price': 55, 'spots': 45},
            {'location': 'Malad Station Plaza', 'address': 'SV Road, Malad West', 'pincode': '400064', 'lat': 19.1864, 'lon': 72.8486, 'price': 50, 'spots': 40},
            {'location': 'Navi Mumbai Hub', 'address': 'Vashi Sector 17', 'pincode': '400703', 'lat': 19.0689, 'lon': 73.0150, 'price': 45, 'spots': 50},
            
            # Delhi NCR (12 locations)
            {'location': 'Connaught Place Central', 'address': 'Inner Circle, CP', 'pincode': '110001', 'lat': 28.6315, 'lon': 77.2167, 'price': 90, 'spots': 40},
            {'location': 'Saket Mall Complex', 'address': 'District Center, Saket', 'pincode': '110017', 'lat': 28.5244, 'lon': 77.2066, 'price': 70, 'spots': 50},
            {'location': 'Rajiv Chowk Metro', 'address': 'Rajiv Chowk', 'pincode': '110001', 'lat': 28.6328, 'lon': 77.2197, 'price': 60, 'spots': 35},
            {'location': 'Dwarka Sector 21', 'address': 'Dwarka Sector 21', 'pincode': '110075', 'lat': 28.5533, 'lon': 77.0590, 'price': 50, 'spots': 45},
            {'location': 'Noida City Centre', 'address': 'Sector 32, Noida', 'pincode': '201301', 'lat': 28.5746, 'lon': 77.3560, 'price': 55, 'spots': 48},
            {'location': 'Gurgaon Cyber Hub', 'address': 'DLF Cyber City', 'pincode': '122002', 'lat': 28.4950, 'lon': 77.0890, 'price': 85, 'spots': 42},
            {'location': 'Karol Bagh Market', 'address': 'Ajmal Khan Road', 'pincode': '110005', 'lat': 28.6519, 'lon': 77.1900, 'price': 65, 'spots': 38},
            {'location': 'Nehru Place IT Hub', 'address': 'Nehru Place', 'pincode': '110019', 'lat': 28.5494, 'lon': 77.2501, 'price': 70, 'spots': 35},
            {'location': 'Lajpat Nagar', 'address': 'Central Market, Lajpat Nagar', 'pincode': '110024', 'lat': 28.5677, 'lon': 77.2437, 'price': 60, 'spots': 40},
            {'location': 'Greater Noida Plaza', 'address': 'Knowledge Park II', 'pincode': '201306', 'lat': 28.4744, 'lon': 77.5040, 'price': 45, 'spots': 50},
            {'location': 'Faridabad Sector 16', 'address': 'NH 19, Faridabad', 'pincode': '121002', 'lat': 28.4089, 'lon': 77.3178, 'price': 40, 'spots': 42},
            {'location': 'Vasant Kunj Mall', 'address': 'Vasant Kunj', 'pincode': '110070', 'lat': 28.5226, 'lon': 77.1563, 'price': 75, 'spots': 45},
            
            # Bangalore (10 locations)
            {'location': 'MG Road Shoppe', 'address': 'MG Road', 'pincode': '560001', 'lat': 12.9762, 'lon': 77.6033, 'price': 75, 'spots': 35},
            {'location': 'Koramangala 5th Block', 'address': '5th Block, Koramangala', 'pincode': '560095', 'lat': 12.9352, 'lon': 77.6193, 'price': 70, 'spots': 40},
            {'location': 'Indiranagar Metro', 'address': 'Indiranagar 100 Ft Road', 'pincode': '560038', 'lat': 12.9718, 'lon': 77.6410, 'price': 65, 'spots': 38},
            {'location': 'Whitefield IT Park', 'address': 'ITPL Main Road', 'pincode': '560066', 'lat': 12.9698, 'lon': 77.7499, 'price': 60, 'spots': 50},
            {'location': 'HSR Layout Sector 1', 'address': 'HSR Layout', 'pincode': '560102', 'lat': 12.9122, 'lon': 77.6381, 'price': 55, 'spots': 42},
            {'location': 'Electronic City Phase 1', 'address': 'Electronic City', 'pincode': '560100', 'lat': 12.8458, 'lon': 77.6593, 'price': 50, 'spots': 45},
            {'location': 'Jayanagar 4th Block', 'address': 'Jayanagar Shopping Complex', 'pincode': '560041', 'lat': 12.9256, 'lon': 77.5952, 'price': 60, 'spots': 35},
            {'location': 'Yeshwanthpur Station', 'address': 'Yeshwanthpur', 'pincode': '560022', 'lat': 13.0280, 'lon': 77.5381, 'price': 50, 'spots': 40},
            {'location': 'Marathahalli Bridge', 'address': 'Outer Ring Road', 'pincode': '560037', 'lat': 12.9591, 'lon': 77.6973, 'price': 55, 'spots': 48},
            {'location': 'Malleshwaram Circle', 'address': '8th Cross, Malleshwaram', 'pincode': '560003', 'lat': 13.0042, 'lon': 77.5709, 'price': 60, 'spots': 35},
            
            # Chennai (8 locations)
            {'location': 'T Nagar Bus Stand', 'address': 'Ranganathan Street', 'pincode': '600017', 'lat': 13.0418, 'lon': 80.2341, 'price': 55, 'spots': 40},
            {'location': 'Anna Nagar Tower', 'address': 'Anna Nagar West', 'pincode': '600040', 'lat': 13.0869, 'lon': 80.2091, 'price': 50, 'spots': 38},
            {'location': 'Velachery MRTS', 'address': 'Velachery Main Road', 'pincode': '600042', 'lat': 12.9750, 'lon': 80.2170, 'price': 45, 'spots': 42},
            {'location': 'Adyar Depot', 'address': 'Lattice Bridge Road', 'pincode': '600020', 'lat': 13.0057, 'lon': 80.2565, 'price': 60, 'spots': 35},
            {'location': 'OMR IT Corridor', 'address': 'Old Mahabalipuram Road', 'pincode': '600096', 'lat': 12.9121, 'lon': 80.2273, 'price': 65, 'spots': 50},
            {'location': 'Porur Junction', 'address': 'Mount-Poonamallee Road', 'pincode': '600116', 'lat': 13.0356, 'lon': 80.1564, 'price': 50, 'spots': 45},
            {'location': 'Guindy Metro Station', 'address': 'Guindy', 'pincode': '600032', 'lat': 13.0093, 'lon': 80.2203, 'price': 55, 'spots': 40},
            {'location': 'Mylapore Temple Area', 'address': 'Luz Church Road', 'pincode': '600004', 'lat': 13.0339, 'lon': 80.2682, 'price': 60, 'spots': 35},
            
            # Hyderabad (8 locations)
            {'location': 'Banjara Hills Road No 12', 'address': 'Road No 12, Banjara Hills', 'pincode': '500034', 'lat': 17.4126, 'lon': 78.4449, 'price': 70, 'spots': 38},
            {'location': 'HITEC City Cyber Gateway', 'address': 'HITEC City', 'pincode': '500081', 'lat': 17.4434, 'lon': 78.3772, 'price': 80, 'spots': 50},
            {'location': 'Secunderabad Railway Station', 'address': 'SP Road', 'pincode': '500003', 'lat': 17.4343, 'lon': 78.5013, 'price': 50, 'spots': 40},
            {'location': 'Gachibowli Financial District', 'address': 'Gachibowli', 'pincode': '500032', 'lat': 17.4401, 'lon': 78.3487, 'price': 75, 'spots': 45},
            {'location': 'Madhapur DLF Plaza', 'address': 'Madhapur', 'pincode': '500081', 'lat': 17.4485, 'lon': 78.3908, 'price': 70, 'spots': 42},
            {'location': 'Kukatpally Housing Board', 'address': 'KPHB Colony', 'pincode': '500072', 'lat': 17.4949, 'lon': 78.3911, 'price': 45, 'spots': 40},
            {'location': 'Jubilee Hills Checkpost', 'address': 'Road No 36, Jubilee Hills', 'pincode': '500033', 'lat': 17.4239, 'lon': 78.4093, 'price': 65, 'spots': 35},
            {'location': 'LB Nagar Metro', 'address': 'LB Nagar', 'pincode': '500074', 'lat': 17.3461, 'lon': 78.5526, 'price': 50, 'spots': 48},
            
            # Pune (6 locations)
            {'location': 'FC Road Market', 'address': 'Fergusson College Road', 'pincode': '411004', 'lat': 18.5196, 'lon': 73.8383, 'price': 60, 'spots': 35},
            {'location': 'Hinjewadi IT Park Phase 1', 'address': 'Hinjewadi', 'pincode': '411057', 'lat': 18.5912, 'lon': 73.7386, 'price': 70, 'spots': 50},
            {'location': 'Kalyani Nagar', 'address': 'Kalyani Nagar', 'pincode': '411006', 'lat': 18.5479, 'lon': 73.9071, 'price': 65, 'spots': 40},
            {'location': 'Koregaon Park', 'address': 'North Main Road', 'pincode': '411001', 'lat': 18.5362, 'lon': 73.8961, 'price': 70, 'spots': 38},
            {'location': 'Wakad Junction', 'address': 'Mumbai-Bangalore Highway', 'pincode': '411057', 'lat': 18.5974, 'lon': 73.7682, 'price': 55, 'spots': 45},
            {'location': 'Deccan Gymkhana', 'address': 'Deccan Gymkhana', 'pincode': '411004', 'lat': 18.5171, 'lon': 73.8422, 'price': 60, 'spots': 42},
            
            # Kolkata (6 locations)
            {'location': 'Park Street Metro', 'address': 'Park Street', 'pincode': '700016', 'lat': 22.5548, 'lon': 88.3516, 'price': 70, 'spots': 38},
            {'location': 'Salt Lake Sector V', 'address': 'Sector V, Salt Lake', 'pincode': '700091', 'lat': 22.5726, 'lon': 88.4324, 'price': 60, 'spots': 50},
            {'location': 'Howrah Station', 'address': 'Howrah', 'pincode': '711101', 'lat': 22.5830, 'lon': 88.3422, 'price': 50, 'spots': 40},
            {'location': 'New Market Area', 'address': 'Lindsay Street', 'pincode': '700087', 'lat': 22.5625, 'lon': 88.3522, 'price': 65, 'spots': 35},
            {'location': 'Rajarhat IT Hub', 'address': 'Rajarhat', 'pincode': '700156', 'lat': 22.6214, 'lon': 88.4609, 'price': 55, 'spots': 45},
            {'location': 'Esplanade Bus Terminal', 'address': 'Esplanade', 'pincode': '700019', 'lat': 22.5646, 'lon': 88.3479, 'price': 60, 'spots': 42},
            
            # Ahmedabad (4 locations)
            {'location': 'SG Highway Business District', 'address': 'SG Highway', 'pincode': '380015', 'lat': 23.0346, 'lon': 72.5085, 'price': 65, 'spots': 45},
            {'location': 'Ashram Road', 'address': 'Ashram Road', 'pincode': '380009', 'lat': 23.0258, 'lon': 72.5873, 'price': 55, 'spots': 40},
            {'location': 'Maninagar Station', 'address': 'Maninagar', 'pincode': '380008', 'lat': 23.0011, 'lon': 72.6017, 'price': 45, 'spots': 38},
            {'location': 'Satellite Jodhpur', 'address': 'Satellite', 'pincode': '380015', 'lat': 23.0262, 'lon': 72.5089, 'price': 60, 'spots': 42},
            
            # Una, Himachal Pradesh (1 location for testing)
            {'location': 'Una Bus Stand', 'address': 'NH 70, Una', 'pincode': '177209', 'lat': 31.4685, 'lon': 76.2708, 'price': 30, 'spots': 35},
        ]
        
        # Create parking lots and spots
        created_lots = []
        for lot_data in parking_lots_data:
            lot_address = Address(
                address=lot_data['address'],
                pincode=lot_data['pincode']
            )
            db.session.add(lot_address)
            db.session.commit()
            
            parking_lot = ParkingLot(
                location=lot_data['location'],
                addressId=lot_address.id,
                totalSpots=lot_data['spots'],
                pricePerHour=lot_data['price'],
                latitude=lot_data['lat'],
                longitude=lot_data['lon']
            )
            db.session.add(parking_lot)
            db.session.commit()
            created_lots.append(parking_lot)
            
            # Create parking spots for this lot
            for spot_num in range(1, lot_data['spots'] + 1):
                # Randomly make some spots occupied (20% occupancy)
                status = 'O' if random.random() < 0.2 else 'A'
                spot = ParkingSpot(
                    lotId=parking_lot.id,
                    spotNumber=spot_num,
                    status=status
                )
                db.session.add(spot)
            
            db.session.commit()
            print(f"✓ Created: {lot_data['location']} ({lot_data['spots']} spots)")
        
        print(f"\n✓ Total parking lots created: {len(created_lots)}")
        
        # Create some sample booking records
        if test_users and created_lots:
            print("\nCreating sample bookings...")
            for i, user in enumerate(test_users[:2]):  # First 2 users get active bookings
                lot = random.choice(created_lots)
                available_spot = ParkingSpot.query.filter_by(
                    lotId=lot.id, status='A'
                ).first()
                
                if available_spot:
                    available_spot.status = 'O'
                    entry_time = datetime.utcnow() - timedelta(hours=random.randint(1, 5))
                    
                    record = ParkingRecord(
                        userId=user.id,
                        vehicleNumber=f'MH{random.randint(10, 99)}XX{random.randint(1000, 9999)}',
                        entryTime=entry_time,
                        exitTime=None,
                        lotId=lot.id,
                        spotId=available_spot.id,
                        bookingPrice=lot.pricePerHour,
                        totalAmountPaid=0,
                        lotLocation=lot.location,
                        lotAddress=lot.address.address,
                        lotPincode=lot.address.pincode
                    )
                    db.session.add(record)
                    print(f"✓ Active booking for {user.name} at {lot.location}")
            
            # Create completed bookings
            for i, user in enumerate(test_users):
                for _ in range(random.randint(1, 3)):
                    lot = random.choice(created_lots)
                    entry_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                    exit_time = entry_time + timedelta(hours=random.randint(2, 8))
                    hours = (exit_time - entry_time).total_seconds() / 3600
                    amount = int(hours * lot.pricePerHour)
                    
                    record = ParkingRecord(
                        userId=user.id,
                        vehicleNumber=f'MH{random.randint(10, 99)}XX{random.randint(1000, 9999)}',
                        entryTime=entry_time,
                        exitTime=exit_time,
                        lotId=lot.id,
                        spotId=None,
                        bookingPrice=lot.pricePerHour,
                        totalAmountPaid=amount,
                        lotLocation=lot.location,
                        lotAddress=lot.address.address,
                        lotPincode=lot.address.pincode
                    )
                    db.session.add(record)
            
            db.session.commit()
            print("✓ Sample bookings created")
        
        db.session.commit()
        print("\n" + "="*60)
        print("✓ Database seeding completed successfully!")
        print("="*60)
        print("\nLogin Credentials:")
        print("-" * 60)
        print("Admin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nTest Users:")
        for user_data in test_users_data:
            print(f"  Username: {user_data['username']}")
            print(f"  Password: {user_data['password']}")
        print("="*60)

if __name__ == '__main__':
    seed_database()
