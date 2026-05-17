"""
Payment and Due Amount Calculation Utilities

This module centralizes all calculations related to resident payments, due amounts,
and overdue status. This ensures consistent calculations between the API endpoints
and serializers.
"""

from decimal import Decimal
from datetime import date, timedelta
import calendar
from django.utils import timezone
from django.db.models import Sum
from .models import Resident, Payment


def get_days_in_month(year: int, month: int) -> int:
    """Get the number of days in a given month/year."""
    return calendar.monthrange(year, month)[1]


def calculate_due_amount(resident: Resident, as_of_date: date = None) -> Decimal:
    """
    Calculate the total due amount for a resident as of a given date.
    
    Includes:
    - Arrears (already overdue from previous periods)
    - Expected rent for completed billing periods minus payments received
    
    For DAILY residents:
        - Rent accrues daily from joining_date
        - Due = (days since joining) × daily_rent - payments_made + arrears
    
    For WEEKLY residents:
        - Rent accrues weekly from joining_date
        - Due = ((days since joining) / 7) × weekly_rent - payments_made + arrears
    
    For MONTHLY residents:
        - Rent due by month (current month NOT included unless move_out_date is past)
        - Due = (full months completed × monthly_rent) - payments_made + arrears
    
    Args:
        resident: Resident instance
        as_of_date: Date to calculate due as of (defaults to today)
    
    Returns:
        Decimal: Total due amount
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    # Base due starts from arrears
    arrears = Decimal(resident.arrears or 0)
    
    # For inactive or without joining date, return only arrears
    if not resident.is_active or not resident.joining_date:
        return arrears
    
    # Cap calculations at move_out_date if set and in the past
    period_end = as_of_date
    if resident.move_out_date and resident.move_out_date <= as_of_date:
        period_end = resident.move_out_date
    
    # Calculate expected rent for billing periods completed
    rent = Decimal(resident.rent or 0)
    expected_total = Decimal(0)
    
    if resident.rent_type == 'daily':
        # Count all days from joining date to today (inclusive)
        # Joining day counts as day 1, so April 24 to May 17 = 24 days
        days = (period_end - resident.joining_date).days + 1
        if days < 0:
            days = 0
        expected_total = rent * Decimal(days)
    
    elif resident.rent_type == 'weekly':
        # Calculate daily rate from weekly rent
        days = (period_end - resident.joining_date).days + 1
        if days < 0:
            days = 0
        daily_rate = rent / Decimal(7)
        expected_total = daily_rate * Decimal(days)
    
    elif resident.rent_type == 'monthly':
        # Count full calendar months from joining month to last month (not current month)
        jy, jm = resident.joining_date.year, resident.joining_date.month
        ly = as_of_date.year if as_of_date.month > 1 else as_of_date.year - 1
        lm = as_of_date.month - 1 if as_of_date.month > 1 else 12
        
        if (jy > ly) or (jy == ly and jm > lm):
            months_until_last = 0
        else:
            months_until_last = (ly - jy) * 12 + (lm - jm) + 1
        
        expected_total = rent * Decimal(months_until_last)
    
    elif resident.rent_type == 'bi-weekly':
        # Calculate daily rate from bi-weekly rent
        days = (period_end - resident.joining_date).days + 1
        if days < 0:
            days = 0
        daily_rate = rent / Decimal(14)
        expected_total = daily_rate * Decimal(days)
    
    # Sum all payments made up to period_end
    paid_total = Decimal(
        Payment.objects.filter(
            resident=resident,
            payment_date__date__lte=period_end
        ).aggregate(total=Sum('amount'))['total'] or 0
    )
    
    # Calculate pending amount
    pending = expected_total - paid_total
    if pending < 0:
        pending = Decimal(0)
    
    # Total due = arrears + pending
    due_total = arrears + pending
    return due_total


def is_overdue(resident: Resident, as_of_date: date = None) -> bool:
    """
    Check if a resident has overdue payments.
    
    For DAILY residents:
        - NOT overdue on joining day (same day)
        - OVERDUE if 1+ full days have passed without payment
    
    For WEEKLY residents:
        - NOT overdue within 7 days
        - OVERDUE if 7+ full days have passed
    
    For MONTHLY residents:
        - OVERDUE if any full calendar month has passed since joining
        - AND payment hasn't covered that month
    
    Args:
        resident: Resident instance
        as_of_date: Date to check as of (defaults to today)
    
    Returns:
        bool: True if resident has overdue payments
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    due_amount = calculate_due_amount(resident, as_of_date)
    
    if due_amount > 0:
        # For daily residents: overdue only if 1+ full days have passed
        # Same day joining = NOT overdue, just DUE
        if resident.rent_type == 'daily':
            if not resident.joining_date:
                return False
            days_since_joining = (as_of_date - resident.joining_date).days
            # Per user requirement: 1-2 days = DUE, 3+ days = OVERDUE
            return days_since_joining >= 3
        
        # For weekly residents, check if a full week has passed
        elif resident.rent_type == 'weekly':
            if not resident.joining_date:
                return False
            days_since_joining = (as_of_date - resident.joining_date).days
            # Overdue if 7+ full days have passed
            return days_since_joining >= 7
        
        # For monthly residents, check if a full month has passed
        elif resident.rent_type == 'monthly':
            if not resident.joining_date:
                return False
            # Overdue if we're past last full month + payment hasn't covered
            last_month_date = as_of_date.replace(day=1) - timedelta(days=1)
            return resident.joining_date <= last_month_date
        
        elif resident.rent_type == 'bi-weekly':
            if not resident.joining_date:
                return False
            days_since_joining = (as_of_date - resident.joining_date).days
            # Overdue if 14+ full days have passed
            return days_since_joining >= 14
    
    return False


def get_overdue_amount(resident: Resident, as_of_date: date = None) -> Decimal:
    """
    Get the overdue amount for a resident.
    
    This is the portion of due_amount that is actually overdue (not due soon).
    
    For DAILY residents:
        - Days overdue × daily_rent (counts only days where payment was due and not made)
    
    For WEEKLY residents:
        - Amounts from weeks that have fully passed
    
    For MONTHLY residents:
        - Amounts from months that have fully passed (up to last month)
    
    Args:
        resident: Resident instance
        as_of_date: Date to calculate as of (defaults to today)
    
    Returns:
        Decimal: Overdue amount
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    if not resident.joining_date or not resident.is_active:
        return Decimal(0)
    
    rent = Decimal(resident.rent or 0)
    
    if resident.rent_type == 'daily':
        # Calculate rent for all days from joining to today (inclusive)
        # Same logic as calculate_due_amount for consistency
        days = (as_of_date - resident.joining_date).days + 1
        if days <= 0:
            return Decimal(0)
        expected = rent * Decimal(days)
    
    elif resident.rent_type == 'weekly':
        days = (as_of_date - resident.joining_date).days
        if days < 7:
            return Decimal(0)
        daily_rate = rent / Decimal(7)
        # Round down to complete weeks
        complete_weeks = days // 7
        expected = daily_rate * Decimal(7) * Decimal(complete_weeks)
    
    elif resident.rent_type == 'monthly':
        # Only count full months up to last month
        jy, jm = resident.joining_date.year, resident.joining_date.month
        if as_of_date.month == 1:
            ly, lm = as_of_date.year - 1, 12
        else:
            ly, lm = as_of_date.year, as_of_date.month - 1
        
        if (jy > ly) or (jy == ly and jm > lm):
            return Decimal(0)
        
        months = (ly - jy) * 12 + (lm - jm) + 1
        expected = rent * Decimal(months)
    
    elif resident.rent_type == 'bi-weekly':
        days = (as_of_date - resident.joining_date).days
        if days < 14:
            return Decimal(0)
        daily_rate = rent / Decimal(14)
        complete_bi_weeks = days // 14
        expected = daily_rate * Decimal(14) * Decimal(complete_bi_weeks)
    
    else:
        return Decimal(0)
    
    # Subtract payments received
    paid = Decimal(
        Payment.objects.filter(
            resident=resident,
            payment_date__date__lte=as_of_date
        ).aggregate(total=Sum('amount'))['total'] or 0
    )
    
    overdue = expected - paid
    if overdue < 0:
        overdue = Decimal(0)
    
    # Add arrears
    overdue += Decimal(resident.arrears or 0)
    
    return overdue


def get_days_overdue(resident: Resident, as_of_date: date = None) -> int:
    """
    Get the number of days a resident is overdue.
    
    Args:
        resident: Resident instance
        as_of_date: Date to calculate as of (defaults to today)
    
    Returns:
        int: Number of days overdue (0 if not overdue)
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    if not resident.joining_date:
        return 0
    
    days_passed = (as_of_date - resident.joining_date).days
    
    if resident.rent_type == 'daily':
        # Overdue if more than 1 day has passed
        return max(0, days_passed)
    
    elif resident.rent_type == 'weekly':
        # Overdue if more than 7 days have passed
        if days_passed < 7:
            return 0
        return days_passed - 6  # Subtract the first 7 days (day 1-7)
    
    elif resident.rent_type == 'monthly':
        # Overdue after a full month
        if days_passed < 30:
            return 0
        return days_passed - 29
    
    elif resident.rent_type == 'bi-weekly':
        # Overdue if more than 14 days have passed
        if days_passed < 14:
            return 0
        return days_passed - 13
    
    return 0


def next_billing_date(resident: Resident, as_of_date: date = None) -> date:
    """
    Calculate the next billing date for a resident.
    
    For DAILY residents:
        - Next billing is tomorrow
    
    For WEEKLY residents:
        - 7 days from last billing
    
    For MONTHLY residents:
        - Uses preferred_billing_day or joining_date.day
    
    Args:
        resident: Resident instance
        as_of_date: Date to calculate from (defaults to today)
    
    Returns:
        date: Next billing date
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    if not resident.joining_date:
        return as_of_date
    
    if resident.rent_type == 'daily':
        return as_of_date + timedelta(days=1)
    
    elif resident.rent_type == 'weekly':
        return as_of_date + timedelta(days=7)
    
    elif resident.rent_type == 'monthly':
        billingday = resident.preferred_billing_day or resident.joining_date.day
        dim_this_month = get_days_in_month(as_of_date.year, as_of_date.month)
        target_day_this_month = min(billingday, dim_this_month)
        this_month_bill = as_of_date.replace(day=target_day_this_month)
        
        if this_month_bill >= as_of_date:
            return this_month_bill
        
        # Next month
        next_month = as_of_date.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        dim_next = get_days_in_month(next_month.year, next_month.month)
        target_day_next = min(billingday, dim_next)
        return next_month.replace(day=target_day_next)
    
    elif resident.rent_type == 'bi-weekly':
        return as_of_date + timedelta(days=14)
    
    return as_of_date
