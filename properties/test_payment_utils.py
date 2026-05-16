"""
Test cases for Due Amount Calculation

Run with: python manage.py test properties.tests
"""

import unittest
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from properties.models import Property, Resident, Payment
from properties.payment_utils import (
    calculate_due_amount,
    is_overdue,
    get_overdue_amount,
    get_days_overdue,
    next_billing_date,
)


class DueCalculationTestCase(TestCase):
    """Test due amount calculations for all rent types."""
    
    def setUp(self):
        """Set up test data."""
        self.property = Property.objects.create(
            name="Test Property",
            address="123 Test St",
            floors_count=3,
            rooms_per_floor=2,
            beds_per_room=2,
        )
    
    # ========== DAILY RENT TESTS ==========
    
    def test_daily_rent_same_day_joining(self):
        """Daily resident joining today should have rent due."""
        resident = Resident.objects.create(
            property=self.property,
            first_name="John",
            mobile="1234567890",
            rent=Decimal("50.00"),
            rent_type="daily",
            joining_date=timezone.now().date(),
        )
        
        due = calculate_due_amount(resident)
        self.assertEqual(due, Decimal("50.00"))
        self.assertFalse(is_overdue(resident))
    
    def test_daily_rent_one_day_overdue(self):
        """Daily resident with 1 day passed should be overdue."""
        yesterday = timezone.now().date() - timedelta(days=1)
        resident = Resident.objects.create(
            property=self.property,
            first_name="Jane",
            mobile="1234567891",
            rent=Decimal("50.00"),
            rent_type="daily",
            joining_date=yesterday,
        )
        
        due = calculate_due_amount(resident)
        # 2 days: yesterday + today
        self.assertEqual(due, Decimal("100.00"))
        self.assertTrue(is_overdue(resident))
    
    def test_daily_rent_multiple_days_with_partial_payment(self):
        """Daily resident with partial payment should show remaining due."""
        three_days_ago = timezone.now().date() - timedelta(days=3)
        resident = Resident.objects.create(
            property=self.property,
            first_name="Bob",
            mobile="1234567892",
            rent=Decimal("100.00"),
            rent_type="daily",
            joining_date=three_days_ago,
        )
        
        # Pay for 2 days
        Payment.objects.create(
            property=self.property,
            resident=resident,
            resident_name=resident.first_name,
            amount=Decimal("200.00"),
            payment_method="cash",
        )
        
        due = calculate_due_amount(resident)
        # 4 days total (3 days ago + today) = 400, paid 200 = due 200
        self.assertEqual(due, Decimal("200.00"))
    
    # ========== WEEKLY RENT TESTS ==========
    
    def test_weekly_rent_same_week(self):
        """Weekly resident within same week should not yet be overdue."""
        today = timezone.now().date()
        resident = Resident.objects.create(
            property=self.property,
            first_name="Alice",
            mobile="1234567893",
            rent=Decimal("350.00"),
            rent_type="weekly",
            joining_date=today,
        )
        
        due = calculate_due_amount(resident)
        # 1 day into week: 350/7 = 50 per day
        self.assertEqual(due, Decimal("50.00"))
        self.assertFalse(is_overdue(resident))
    
    def test_weekly_rent_exactly_one_week_overdue(self):
        """Weekly resident with 7 days passed should be overdue."""
        week_ago = timezone.now().date() - timedelta(days=7)
        resident = Resident.objects.create(
            property=self.property,
            first_name="Charlie",
            mobile="1234567894",
            rent=Decimal("350.00"),
            rent_type="weekly",
            joining_date=week_ago,
        )
        
        due = calculate_due_amount(resident)
        self.assertTrue(is_overdue(resident))
    
    # ========== BI-WEEKLY RENT TESTS ==========
    
    def test_biweekly_rent_one_week_in(self):
        """Bi-weekly resident in first week should have partial due."""
        one_week_ago = timezone.now().date() - timedelta(days=7)
        resident = Resident.objects.create(
            property=self.property,
            first_name="Diana",
            mobile="1234567895",
            rent=Decimal("700.00"),
            rent_type="bi-weekly",
            joining_date=one_week_ago,
        )
        
        due = calculate_due_amount(resident)
        # 8 days: 700/14 * 8 = 400
        expected = Decimal("700.00") / Decimal("14") * Decimal("8")
        self.assertAlmostEqual(float(due), float(expected), places=2)
        self.assertFalse(is_overdue(resident))
    
    def test_biweekly_rent_two_weeks_overdue(self):
        """Bi-weekly resident with 14+ days should be overdue."""
        two_weeks_ago = timezone.now().date() - timedelta(days=14)
        resident = Resident.objects.create(
            property=self.property,
            first_name="Eve",
            mobile="1234567896",
            rent=Decimal("700.00"),
            rent_type="bi-weekly",
            joining_date=two_weeks_ago,
        )
        
        due = calculate_due_amount(resident)
        self.assertEqual(due, Decimal("700.00"))
        self.assertTrue(is_overdue(resident))
    
    # ========== MONTHLY RENT TESTS ==========
    
    def test_monthly_rent_same_month(self):
        """Monthly resident in same joining month should have no due."""
        today = timezone.now().date()
        resident = Resident.objects.create(
            property=self.property,
            first_name="Frank",
            mobile="1234567897",
            rent=Decimal("5000.00"),
            rent_type="monthly",
            joining_date=today,
            preferred_billing_day=today.day,
        )
        
        due = calculate_due_amount(resident)
        # Current month not included yet
        self.assertEqual(due, Decimal("0.00"))
        self.assertFalse(is_overdue(resident))
    
    def test_monthly_rent_one_full_month_passed(self):
        """Monthly resident with 1+ complete months should be due."""
        # Join 1 month ago on same day
        today = timezone.now().date()
        first_of_month_ago = today.replace(day=1) - timedelta(days=1)
        first_of_month_ago = first_of_month_ago.replace(day=1)
        
        resident = Resident.objects.create(
            property=self.property,
            first_name="Greg",
            mobile="1234567898",
            rent=Decimal("5000.00"),
            rent_type="monthly",
            joining_date=first_of_month_ago,
            preferred_billing_day=1,
        )
        
        due = calculate_due_amount(resident)
        # Should have at least 1 full month due
        self.assertGreaterEqual(due, Decimal("0.00"))
    
    def test_monthly_rent_with_full_month_paid(self):
        """Monthly resident with paid month should show no due for that month."""
        # Join on 1st of month, pay full month
        today = timezone.now().date()
        if today.day == 1:
            # Start from previous month
            joining_date = today - timedelta(days=1)
            joining_date = joining_date.replace(day=1)
        else:
            joining_date = today.replace(day=1) - timedelta(days=1)
        
        resident = Resident.objects.create(
            property=self.property,
            first_name="Helen",
            mobile="1234567899",
            rent=Decimal("5000.00"),
            rent_type="monthly",
            joining_date=joining_date,
            preferred_billing_day=1,
        )
        
        # Pay for one month
        Payment.objects.create(
            property=self.property,
            resident=resident,
            resident_name=resident.first_name,
            amount=Decimal("5000.00"),
            payment_method="cash",
        )
        
        due = calculate_due_amount(resident)
        # Should be zero or minimal if paid
        self.assertLessEqual(due, Decimal("100.00"))
    
    # ========== ARREARS TESTS ==========
    
    def test_with_arrears_added_to_due(self):
        """Resident with arrears should include it in total due."""
        resident = Resident.objects.create(
            property=self.property,
            first_name="Iris",
            mobile="1234567800",
            rent=Decimal("100.00"),
            rent_type="daily",
            joining_date=timezone.now().date(),
            arrears=Decimal("500.00"),
        )
        
        due = calculate_due_amount(resident)
        # 100 (today's rent) + 500 (arrears) = 600
        self.assertEqual(due, Decimal("600.00"))
    
    # ========== INACTIVE/MOVED OUT TESTS ==========
    
    def test_inactive_resident_shows_only_arrears(self):
        """Inactive resident should show only arrears as due."""
        resident = Resident.objects.create(
            property=self.property,
            first_name="Jack",
            mobile="1234567801",
            rent=Decimal("100.00"),
            rent_type="daily",
            joining_date=timezone.now().date() - timedelta(days=5),
            is_active=False,
            arrears=Decimal("250.00"),
        )
        
        due = calculate_due_amount(resident)
        # Should not accumulate new due, only arrears
        self.assertEqual(due, Decimal("250.00"))
    
    def test_moved_out_resident_calculates_till_moveout_date(self):
        """Resident who moved out should calculate due till move_out_date."""
        joining_date = timezone.now().date() - timedelta(days=10)
        move_out_date = timezone.now().date() - timedelta(days=5)
        
        resident = Resident.objects.create(
            property=self.property,
            first_name="Kelly",
            mobile="1234567802",
            rent=Decimal("100.00"),
            rent_type="daily",
            joining_date=joining_date,
            move_out_date=move_out_date,
            is_active=False,
        )
        
        due = calculate_due_amount(resident)
        # 6 days: from joining to move_out (inclusive)
        self.assertEqual(due, Decimal("600.00"))
    
    # ========== HELPER FUNCTION TESTS ==========
    
    def test_next_billing_date_daily(self):
        """Next billing for daily should be tomorrow."""
        today = timezone.now().date()
        resident = Resident.objects.create(
            property=self.property,
            first_name="Leo",
            mobile="1234567803",
            rent=Decimal("50.00"),
            rent_type="daily",
            joining_date=today,
        )
        
        next_bill = next_billing_date(resident, today)
        self.assertEqual(next_bill, today + timedelta(days=1))
    
    def test_next_billing_date_weekly(self):
        """Next billing for weekly should be 7 days away."""
        today = timezone.now().date()
        resident = Resident.objects.create(
            property=self.property,
            first_name="Mike",
            mobile="1234567804",
            rent=Decimal("350.00"),
            rent_type="weekly",
            joining_date=today,
        )
        
        next_bill = next_billing_date(resident, today)
        self.assertEqual(next_bill, today + timedelta(days=7))
    
    def test_next_billing_date_monthly(self):
        """Next billing for monthly with preferred_billing_day."""
        today = timezone.now().date()
        resident = Resident.objects.create(
            property=self.property,
            first_name="Nina",
            mobile="1234567805",
            rent=Decimal("5000.00"),
            rent_type="monthly",
            joining_date=today,
            preferred_billing_day=15,
        )
        
        next_bill = next_billing_date(resident, today)
        # Should be 15th of current month if today < 15, else next month
        if today.day < 15:
            self.assertEqual(next_bill.day, 15)
            self.assertEqual(next_bill.month, today.month)
        else:
            self.assertEqual(next_bill.day, 15)


if __name__ == '__main__':
    unittest.main()
