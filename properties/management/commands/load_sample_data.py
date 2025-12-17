from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from properties.models import (
    Property, Floor, Room, Bed, Resident, Occupancy, OccupancyHistory,
    Expense, Payment, MaintenanceRequest, User
)


class Command(BaseCommand):
    help = 'Load sample data into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Loading sample data...'))

        # Create Properties
        prop1, _ = Property.objects.get_or_create(
            name='Grand View Residency',
            defaults={
                'address': '123 Main Street',
                'city': 'New York',
                'state': 'NY',
                'zip_code': '10001',
                'floors_count': 5,
                'rooms_per_floor': 2,
                'beds_per_room': 3,
                'description': 'Premium residential property',
            }
        )

        prop2, _ = Property.objects.get_or_create(
            name='Oak Park Apartments',
            defaults={
                'address': '456 Oak Avenue',
                'city': 'Los Angeles',
                'state': 'CA',
                'zip_code': '90001',
                'floors_count': 4,
                'rooms_per_floor': 3,
                'beds_per_room': 2,
                'description': 'Modern apartment complex',
            }
        )

        # Create Floors
        floor1, _ = Floor.objects.get_or_create(
            property=prop1,
            floor_level=1,
            defaults={'floor_name': 'Ground Floor'}
        )
        
        floor2, _ = Floor.objects.get_or_create(
            property=prop1,
            floor_level=2,
            defaults={'floor_name': 'First Floor'}
        )

        # Create Rooms
        room1, _ = Room.objects.get_or_create(
            floor=floor1,
            property=prop1,
            room_number='101',
            defaults={
                'room_name': 'Room A',
                'total_beds': 3,
                'room_type': 'triple',
                'capacity': 3,
            }
        )

        room2, _ = Room.objects.get_or_create(
            floor=floor1,
            property=prop1,
            room_number='102',
            defaults={
                'room_name': 'Room B',
                'total_beds': 2,
                'room_type': 'double',
                'capacity': 2,
            }
        )

        # Create Beds
        bed1, _ = Bed.objects.get_or_create(
            room=room1,
            floor=floor1,
            property=prop1,
            bed_number='101A',
            defaults={'bed_name': 'Bed 1A'}
        )

        bed2, _ = Bed.objects.get_or_create(
            room=room1,
            floor=floor1,
            property=prop1,
            bed_number='101B',
            defaults={'bed_name': 'Bed 1B'}
        )

        # Create Residents
        today = timezone.now().date()
        resident1, _ = Resident.objects.get_or_create(
            property=prop1,
            mobile='9876543210',
            defaults={
                'name': 'Rajesh Kumar',
                'gender': 'M',
                'email': 'rajesh@example.com',
                'rent': 5000,
                'rent_type': 'monthly',
                'joining_date': today - timedelta(days=30),
                'next_pay_date': today + timedelta(days=10),
                'current_floor': floor1,
                'current_room': room1,
                'current_bed': bed1,
            }
        )

        resident2, _ = Resident.objects.get_or_create(
            property=prop1,
            mobile='9123456789',
            defaults={
                'name': 'Priya Singh',
                'gender': 'F',
                'email': 'priya@example.com',
                'rent': 4500,
                'rent_type': 'monthly',
                'joining_date': today - timedelta(days=60),
                'next_pay_date': today - timedelta(days=5),
                'current_floor': floor1,
                'current_room': room1,
                'current_bed': bed2,
            }
        )

        # Create Occupancy records
        Occupancy.objects.get_or_create(
            property=prop1,
            floor=floor1,
            room=room1,
            bed=bed1,
            defaults={
                'resident': resident1,
                'is_occupied': True,
                'occupied_since': today - timedelta(days=30),
            }
        )

        Occupancy.objects.get_or_create(
            property=prop1,
            floor=floor1,
            room=room1,
            bed=bed2,
            defaults={
                'resident': resident2,
                'is_occupied': True,
                'occupied_since': today - timedelta(days=60),
            }
        )

        # Create Expenses
        Expense.objects.get_or_create(
            property=prop1,
            category='Electricity',
            description='Monthly electricity bill',
            expense_date=today,
            defaults={
                'amount': 1200,
                'paid_by': 'Manager',
                'payment_method': 'bank_transfer',
            }
        )

        Expense.objects.get_or_create(
            property=prop1,
            category='Maintenance',
            description='Plumbing repair',
            expense_date=today - timedelta(days=5),
            defaults={
                'amount': 500,
                'paid_by': 'Manager',
                'payment_method': 'cash',
            }
        )

        # Create Payments
        Payment.objects.get_or_create(
            property=prop1,
            resident=resident1,
            resident_name=resident1.name,
            defaults={
                'amount': 5000,
                'payment_method': 'bank_transfer',
                'reference_number': 'PAY001',
            }
        )

        Payment.objects.get_or_create(
            property=prop1,
            resident=resident2,
            resident_name=resident2.name,
            defaults={
                'amount': 4500,
                'payment_method': 'upi',
                'reference_number': 'PAY002',
            }
        )

        # Create Maintenance Requests
        MaintenanceRequest.objects.get_or_create(
            property=prop1,
            category='Electrical',
            description='Broken light in room 101',
            defaults={
                'priority': 'high',
                'status': 'open',
                'estimated_cost': 200,
            }
        )

        MaintenanceRequest.objects.get_or_create(
            property=prop1,
            category='Plumbing',
            description='Leaky tap in bathroom',
            defaults={
                'priority': 'medium',
                'status': 'in_progress',
                'estimated_cost': 500,
            }
        )

        # Create Users
        User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@pgadmin.com',
                'password_hash': 'hashed_password',
                'role': 'admin',
            }
        )

        User.objects.get_or_create(
            username='manager',
            defaults={
                'email': 'manager@pgadmin.com',
                'password_hash': 'hashed_password',
                'role': 'manager',
                'property': prop1,
            }
        )

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))
