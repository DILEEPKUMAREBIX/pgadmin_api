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


def _add_months_keep_day(base_date: date, months: int) -> date:
    """Add months to a date while clamping day to the target month's max day."""
    month_index = (base_date.month - 1) + months
    year = base_date.year + (month_index // 12)
    month = (month_index % 12) + 1
    day = min(base_date.day, get_days_in_month(year, month))
    return date(year, month, day)


def _count_monthly_cycles_started(joining_date: date, period_end: date) -> int:
    """Count started monthly billing cycles between joining_date and period_end (inclusive)."""
    if period_end < joining_date:
        return 0

    cycles = 1
    cycle_start = joining_date
    while True:
        next_cycle_start = _add_months_keep_day(cycle_start, 1)
        if next_cycle_start <= period_end:
            cycles += 1
            cycle_start = next_cycle_start
            continue
        break

    return cycles


def calculate_checkout_breakdown(
    resident: Resident,
    as_of_date: date = None,
    monthly_option: str = 'rounded_month',
) -> dict:
    """
    Build a detailed due breakdown for resident checkout.

    Formula used:
    - MONTHLY: (number_of_monthly_cycles_started * monthly_rent) + arrears - payments_till_checkout
    - DAILY: (days_stayed * daily_rent) + arrears - payments_till_checkout
    - WEEKLY: ((days_stayed / 7) * weekly_rent) + arrears - payments_till_checkout
    - BI-WEEKLY: ((days_stayed / 14) * bi_weekly_rent) + arrears - payments_till_checkout
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()

    arrears = Decimal(resident.arrears or 0)
    rent = Decimal(resident.rent or 0)
    joining_date = resident.joining_date

    period_end = as_of_date
    if resident.move_out_date and resident.move_out_date < period_end:
        period_end = resident.move_out_date

    payments_qs = Payment.objects.filter(
        resident=resident,
        payment_date__date__lte=period_end
    ).order_by('payment_date')
    paid_total = Decimal(payments_qs.aggregate(total=Sum('amount'))['total'] or 0)

    expected_rent = Decimal(0)
    period_count = 0
    period_type = resident.rent_type
    daily_rate = None

    if joining_date and period_end >= joining_date:
        days_stayed = (period_end - joining_date).days + 1
    else:
        days_stayed = 0

    monthly_options = None

    if period_type == 'monthly':
        months_started = _count_monthly_cycles_started(joining_date, period_end) if joining_date else 0
        full_months_completed = max(0, months_started - 1)

        if joining_date and period_end >= joining_date:
            current_cycle_start = _add_months_keep_day(joining_date, full_months_completed)
            extra_days = (period_end - current_cycle_start).days + 1
            if extra_days < 0:
                extra_days = 0
        else:
            extra_days = 0

        daily_rate = rent / Decimal(30) if rent else Decimal(0)

        expected_rent_rounded = rent * Decimal(months_started)
        expected_rent_prorated = (rent * Decimal(full_months_completed)) + (daily_rate * Decimal(extra_days))

        due_rounded = expected_rent_rounded + arrears - paid_total
        if due_rounded < 0:
            due_rounded = Decimal(0)

        due_prorated = expected_rent_prorated + arrears - paid_total
        if due_prorated < 0:
            due_prorated = Decimal(0)

        monthly_options = {
            'rounded_month': {
                'label': 'Consider started month as full month',
                'expected_rent': str(expected_rent_rounded.quantize(Decimal('0.01'))),
                'remaining_due': str(due_rounded.quantize(Decimal('0.01'))),
                'formula': 'expected_rent = monthly_cycles_started * monthly_rent',
                'formula_values': {
                    'monthly_cycles_started': months_started,
                    'monthly_rent': str(rent.quantize(Decimal('0.01'))),
                },
            },
            'prorated_days': {
                'label': 'Full months + extra days by day charge',
                'expected_rent': str(expected_rent_prorated.quantize(Decimal('0.01'))),
                'remaining_due': str(due_prorated.quantize(Decimal('0.01'))),
                'formula': 'expected_rent = (full_months_completed * monthly_rent) + (extra_days * (monthly_rent / 30))',
                'formula_values': {
                    'full_months_completed': full_months_completed,
                    'extra_days': extra_days,
                    'monthly_rent': str(rent.quantize(Decimal('0.01'))),
                    'daily_rate': str(daily_rate.quantize(Decimal('0.01'))),
                },
            },
        }

        if monthly_option == 'prorated_days':
            expected_rent = expected_rent_prorated
            due_amount = due_prorated
            formula = monthly_options['prorated_days']['formula']
            formula_values = monthly_options['prorated_days']['formula_values']
            period_count = full_months_completed
        else:
            expected_rent = expected_rent_rounded
            due_amount = due_rounded
            formula = monthly_options['rounded_month']['formula']
            formula_values = monthly_options['rounded_month']['formula_values']
            period_count = months_started
    elif period_type == 'daily':
        period_count = days_stayed
        expected_rent = rent * Decimal(days_stayed)
        formula = 'expected_rent = days_stayed * daily_rent'
        formula_values = {
            'days_stayed': days_stayed,
            'daily_rent': str(rent.quantize(Decimal('0.01'))),
        }
    elif period_type == 'weekly':
        period_count = days_stayed
        daily_rate = rent / Decimal(7) if rent else Decimal(0)
        expected_rent = daily_rate * Decimal(days_stayed)
        formula = 'expected_rent = (days_stayed / 7) * weekly_rent'
        formula_values = {
            'days_stayed': days_stayed,
            'weekly_rent': str(rent.quantize(Decimal('0.01'))),
            'daily_rate': str(daily_rate.quantize(Decimal('0.01'))),
        }
    elif period_type == 'bi-weekly':
        period_count = days_stayed
        daily_rate = rent / Decimal(14) if rent else Decimal(0)
        expected_rent = daily_rate * Decimal(days_stayed)
        formula = 'expected_rent = (days_stayed / 14) * bi_weekly_rent'
        formula_values = {
            'days_stayed': days_stayed,
            'bi_weekly_rent': str(rent.quantize(Decimal('0.01'))),
            'daily_rate': str(daily_rate.quantize(Decimal('0.01'))),
        }
    else:
        formula = 'Unsupported rent_type; expected_rent set to 0.'
        formula_values = {}

    if period_type != 'monthly':
        raw_due = expected_rent + arrears - paid_total
        due_amount = raw_due if raw_due > 0 else Decimal(0)
    else:
        raw_due = expected_rent + arrears - paid_total

    explanation = [
        f"Rent type: {resident.rent_type}",
        f"Expected rent till {period_end.isoformat()} calculated using: {formula}",
        f"Total due = expected_rent ({expected_rent.quantize(Decimal('0.01'))}) + arrears ({arrears.quantize(Decimal('0.01'))}) - payments ({paid_total.quantize(Decimal('0.01'))})",
    ]
    if raw_due <= 0:
        explanation.append('Resident has no pending due after payments adjustment.')

    payment_breakdown = [
        {
            'id': payment.id,
            'amount': str(Decimal(payment.amount).quantize(Decimal('0.01'))),
            'payment_date': payment.payment_date.isoformat(),
            'payment_method': payment.payment_method,
            'reference_number': payment.reference_number,
        }
        for payment in payments_qs
    ]

    if period_type == 'monthly':
        explanation.append(
            'Monthly checkout options are provided. UI can choose rounded_month or prorated_days for final settlement.'
        )

    return {
        'resident_id': resident.id,
        'resident_name': resident.name,
        'rent_type': resident.rent_type,
        'joining_date': joining_date.isoformat() if joining_date else None,
        'checkout_date': as_of_date.isoformat(),
        'calculation_period_end': period_end.isoformat(),
        'days_stayed': days_stayed,
        'period_count': period_count,
        'rent_per_period': str(rent.quantize(Decimal('0.01'))),
        'expected_rent': str(expected_rent.quantize(Decimal('0.01'))),
        'arrears': str(arrears.quantize(Decimal('0.01'))),
        'payments_till_checkout': str(paid_total.quantize(Decimal('0.01'))),
        'remaining_due': str(due_amount.quantize(Decimal('0.01'))),
        'applied_monthly_option': monthly_option if period_type == 'monthly' else None,
        'monthly_checkout_options': monthly_options,
        'formula': formula,
        'formula_values': formula_values,
        'explanation': explanation,
        'payment_count': payments_qs.count(),
        'payments': payment_breakdown,
    }


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
    
    # Calculate total due
    due_total = expected_total + arrears - paid_total
    if due_total < 0:
        due_total = Decimal(0)
    
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
