from rest_framework import viewsets, filters, status
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password, check_password
from core.auth import generate_jwt
from .serializers import (
    AuthRegisterSerializer, AuthLoginSerializer, AuthTokenResponseSerializer, AuthUserMiniSerializer
)
from .models import (
    Property, Floor, Room, Bed, Resident, Occupancy, OccupancyHistory,
    Expense, Payment, MaintenanceRequest, User
)
from .serializers import (
    PropertySerializer, FloorSerializer, RoomSerializer, BedSerializer,
    ResidentSerializer, OccupancySerializer, OccupancyHistorySerializer,
    ExpenseSerializer, PaymentSerializer, MaintenanceRequestSerializer,
    UserSerializer, PropertyOccupancyDetailSerializer
)


@extend_schema(tags=['Properties'])
class PropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing properties.
    
    - List all properties
    - Create new property
    - Retrieve property details
    - Update property information
    - Delete property
    - Get property summary with statistics
    - Get consolidated occupancy details with floors, rooms, and bed status
    """
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'city', 'state']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get property summary with occupancy and payment stats"""
        property_obj = self.get_object()
        data = {
            'id': property_obj.id,
            'name': property_obj.name,
            'total_beds': property_obj.total_beds,
            'occupied_beds': property_obj.occupancies.filter(is_occupied=True).count(),
            'available_beds': property_obj.occupancies.filter(is_occupied=False).count(),
            'active_residents': property_obj.residents.filter(is_active=True).count(),
            'total_residents': property_obj.residents.count(),
        }
        return Response(data)

    @action(detail=True, methods=['get'])
    def occupancy_detail(self, request, pk=None):
        """
        Get consolidated property details with complete occupancy information.
        
        Returns:
        - Property basic details (name, address, etc.)
        - All floors in the property
        - All rooms per floor with room details
        - All beds per room with occupancy status
        - Resident information for occupied beds
        - Occupancy statistics at property, floor, and room levels
        
        Perfect for mobile app occupancy tab display.
        """
        property_obj = self.get_object()
        serializer = PropertyOccupancyDetailSerializer(property_obj)
        return Response(serializer.data)

    @extend_schema(
        tags=['Payments'],
        description='List all payments for this property with resident details. Optional filters: start_date, end_date (YYYY-MM-DD).',
        parameters=[
            OpenApiParameter(name='start_date', description='Start date (YYYY-MM-DD)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='end_date', description='End date (YYYY-MM-DD)', required=False, type=OpenApiTypes.STR),
        ]
    )
    @action(detail=True, methods=['get'], url_path='payments')
    def payments(self, request, pk=None):
        """All payments for the property, including resident info."""
        from datetime import datetime

        property_obj = self.get_object()
        qs = Payment.objects.filter(property=property_obj).order_by('-payment_date')

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            try:
                sd = datetime.strptime(start_date, '%Y-%m-%d').date()
                qs = qs.filter(payment_date__date__gte=sd)
            except ValueError:
                return Response({'detail': 'Invalid start_date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        if end_date:
            try:
                ed = datetime.strptime(end_date, '%Y-%m-%d').date()
                qs = qs.filter(payment_date__date__lte=ed)
            except ValueError:
                return Response({'detail': 'Invalid end_date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentSerializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(tags=['Home'], description='Home screen summary for a property')
    @action(detail=True, methods=['get'])
    def home_summary(self, request, pk=None):
        from django.utils import timezone
        from django.db.models import Sum
        from datetime import date, timedelta

        property_obj = self.get_object()
        today = timezone.now().date()

        def days_in_month(y: int, m: int):
            import calendar
            return calendar.monthrange(y, m)[1]

        def billing_day_for(res: Resident):
            # Use preferred_billing_day if set, else joining day
            day = res.preferred_billing_day or (res.joining_date.day if res.joining_date else None)
            if not day:
                return None
            # Clamp to valid day for month when computing actual dates
            return day

        def next_installment_date(res: Resident):
            bday = billing_day_for(res)
            if not bday:
                return None
            dim = days_in_month(today.year, today.month)
            target_day_this_month = min(bday, dim)
            this_month_due = date(today.year, today.month, target_day_this_month)
            if this_month_due >= today:
                return this_month_due
            # Next month
            ny = today.year + 1 if today.month == 12 else today.year
            nm = 1 if today.month == 12 else today.month + 1
            dim_next = days_in_month(ny, nm)
            target_day_next = min(bday, dim_next)
            return date(ny, nm, target_day_next)

        # Helper: count calendar months from join month to last month inclusive
        def month_count_until_last_month(res: Resident):
            if not res.joining_date:
                return 0
            # Last month end
            if today.month == 1:
                last_month_year = today.year - 1
                last_month = 12
            else:
                last_month_year = today.year
                last_month = today.month - 1
            # If joining month is after last month, zero
            jm = res.joining_date.month
            jy = res.joining_date.year
            if (jy > last_month_year) or (jy == last_month_year and jm > last_month):
                return 0
            return (last_month_year - jy) * 12 + (last_month - jm) + 1

        # Active monthly residents
        residents_monthly = Resident.objects.filter(
            property=property_obj,
            is_active=True,
            move_out_date__isnull=True,
            rent_type='monthly',
        )

        # Compute overdue based on full months up to last month (ignore current month)
        overdue_residents = []
        overdue_details = []  # per-resident with overdue_amount
        overdue_total_amount = 0.0
        # Determine last month end date for payment cutoff
        if today.month == 1:
            lmy, lmm = today.year - 1, 12
        else:
            lmy, lmm = today.year, today.month - 1
        lmdim = days_in_month(lmy, lmm)
        last_month_end = date(lmy, lmm, lmdim)

        for res in residents_monthly:
            months = month_count_until_last_month(res)
            expected = float(res.rent) * months
            # Payments made till date (use amount field)
            paid = Payment.objects.filter(resident=res, payment_date__date__lte=today).aggregate(total=Sum('amount'))['total'] or 0
            paid = float(paid)
            # Include resident-level arrears on top of computed pending
            pending = max(0.0, expected - paid) + float(getattr(res, 'arrears', 0) or 0)
            if pending > 0:
                overdue_residents.append(res)
                data = ResidentSerializer(res).data
                data['overdue_amount'] = round(pending, 2)
                overdue_details.append(data)
                overdue_total_amount += pending

        # Compute due soon (next installment within 5 days)
        due_soon_residents = []
        due_soon_total_amount = 0.0
        for res in residents_monthly:
            nxt = next_installment_date(res)
            if not nxt:
                continue
            delta_days = (nxt - today).days
            if 0 <= delta_days <= 5:
                due_soon_residents.append(res)
                due_soon_total_amount += float(res.rent)

        # Beds summary
        occupied_beds = Occupancy.objects.filter(property=property_obj, is_occupied=True).count()
        # 'available' should reflect total beds in the property (not free beds)
        # Filter beds via room -> floor -> property to avoid cross-property counts
        available_beds = Bed.objects.filter(room__floor__property=property_obj).count()

        # Expenses
        year_start = today.replace(month=1, day=1)
        month_start = today.replace(day=1)
        expenses_year = Expense.objects.filter(property=property_obj, expense_date__date__gte=year_start, expense_date__date__lte=today).aggregate(Sum('amount'))
        expenses_month = Expense.objects.filter(property=property_obj, expense_date__date__gte=month_start, expense_date__date__lte=today).aggregate(Sum('amount'))

        return Response({
            'property': {
                'id': property_obj.id,
                'name': property_obj.name,
            },
            'beds': {
                'occupied': occupied_beds,
                'available': available_beds,
            },
            'overdue': {
                'count': len(overdue_residents),
                'total_amount': round(overdue_total_amount, 2),
                'residents': overdue_details,
            },
            'due_soon': {
                'count': len(due_soon_residents),
                'total_amount': round(due_soon_total_amount, 2),
                'residents': ResidentSerializer(due_soon_residents, many=True).data,
            },
            'expenses': {
                'year_total': float(expenses_year['amount__sum'] or 0),
                'month_total': float(expenses_month['amount__sum'] or 0),
            }
        })

    @extend_schema(
        tags=['Finance'],
        description='Financial summary for the last 5 years with monthly income (payments) and expenses. Returns per-year totals and top spending categories.'
    )
    @action(detail=True, methods=['get'], url_path='financial_summary')
    def financial_summary(self, request, pk=None):
        from django.utils import timezone
        from django.db.models import Sum
        from django.db.models.functions import ExtractMonth

        property_obj = self.get_object()
        current_year = timezone.now().date().year
        years = [current_year - i for i in range(0, 5)]

        results = []
        for year in years:
            # Monthly income (payments)
            income_rows = (
                Payment.objects
                .filter(property=property_obj, payment_date__year=year)
                .annotate(month=ExtractMonth('payment_date'))
                .values('month')
                .annotate(total=Sum('amount'))
            )
            income_series = [0.0] * 12
            for row in income_rows:
                m = row['month']
                if 1 <= m <= 12:
                    income_series[m - 1] = float(row['total'] or 0)

            # Monthly expenses
            expense_rows = (
                Expense.objects
                .filter(property=property_obj, expense_date__year=year)
                .annotate(month=ExtractMonth('expense_date'))
                .values('month')
                .annotate(total=Sum('amount'))
            )
            expense_series = [0.0] * 12
            for row in expense_rows:
                m = row['month']
                if 1 <= m <= 12:
                    expense_series[m - 1] = float(row['total'] or 0)

            # Totals for the year
            total_income = float(
                Payment.objects.filter(property=property_obj, payment_date__year=year).aggregate(Sum('amount'))['amount__sum'] or 0
            )
            total_expenses = float(
                Expense.objects.filter(property=property_obj, expense_date__year=year).aggregate(Sum('amount'))['amount__sum'] or 0
            )

            # Top spendings by category (top 5)
            top_categories_qs = (
                Expense.objects
                .filter(property=property_obj, expense_date__year=year)
                .values('category')
                .annotate(total=Sum('amount'))
                .order_by('-total')[:5]
            )
            top_categories = [{'category': r['category'], 'total': float(r['total'] or 0)} for r in top_categories_qs]

            # Resident stats for the year
            joined_count = Resident.objects.filter(property=property_obj, joining_date__year=year).count()
            moved_out_count = Resident.objects.filter(property=property_obj, move_out_date__year=year).count()

            results.append({
                'year': year,
                'monthly': {
                    'income': income_series,
                    'expenses': expense_series,
                },
                'totals': {
                    'income': total_income,
                    'expenses': total_expenses,
                    'net': round(total_income - total_expenses, 2),
                },
                'top_spendings': {
                    'categories': top_categories,
                },
                'residents': {
                    'joined': joined_count,
                    'moved_out': moved_out_count,
                },
            })

        return Response({
            'property': {
                'id': property_obj.id,
                'name': property_obj.name,
            },
            'years': results,
        })


@extend_schema(tags=['Floors'])
class FloorViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing floors within properties.
    
    - List floors by a property
    - Create new floor
    - Retrieve floor details
    - Update floor information
    - Delete floor
    """
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'is_active', 'floor_level']
    ordering_fields = ['floor_level', 'created_at']
    ordering = ['property', 'floor_level']


@extend_schema(tags=['Rooms'])
class RoomViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing rooms within floors.
    
    - List rooms by floor/property
    - Create new room
    - Retrieve room details
    - Update room information
    - Delete room
    """
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'floor', 'is_active', 'room_type']
    search_fields = ['room_number', 'room_name']
    ordering_fields = ['room_number', 'created_at']
    ordering = ['floor', 'room_number']


@extend_schema(tags=['Beds'])
class BedViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing beds within rooms.
    
    - List beds by room/property
    - Create new bed
    - Retrieve bed details
    - Update bed information
    - Delete bed
    - Get available beds
    """
    queryset = Bed.objects.all()
    serializer_class = BedSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'floor', 'room', 'is_active']
    search_fields = ['bed_number', 'bed_name']
    ordering_fields = ['bed_number', 'created_at']
    ordering = ['room', 'bed_number']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available beds"""
        available_beds = Bed.objects.filter(is_active=True, occupancy__is_occupied=False)
        serializer = self.get_serializer(available_beds, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Residents'])
class ResidentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing residents/tenants.
    
    - List all residents
    - Create new resident
    - Retrieve resident details
    - Update resident information
    - Delete resident
    - Get residents with payment due soon
    """
    queryset = Resident.objects.all()
    serializer_class = ResidentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'is_active', 'rent_type']
    search_fields = ['first_name', 'last_name', 'email', 'mobile']
    ordering_fields = ['first_name', 'last_name', 'joining_date', 'preferred_billing_day', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Default: return only active residents (move_out_date is NULL).
        To include moved-out residents as well, pass query `include_moved_out=true`.
        To fetch only moved-out residents via this endpoint, pass `moved_out_only=true`
        (Alternatively, use `/residents/historical/`).
        """
        qs = Resident.objects.all()
        params = self.request.query_params
        moved_out_only = params.get('moved_out_only')
        include_moved_out = params.get('include_moved_out')
        if moved_out_only and moved_out_only.lower() in ('1', 'true', 'yes'):  # only moved out
            return qs.filter(move_out_date__isnull=False)
        if include_moved_out and include_moved_out.lower() in ('1', 'true', 'yes'):  # include all
            return qs
        # default: active only
        return qs.filter(is_active=True, move_out_date__isnull=True)

    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        """Get residents with billing day within next 7 days"""
        from django.utils import timezone
        
        today = timezone.now().date()
        d0 = today.day
        d7 = (d0 + 7)

        qs = Resident.objects.filter(is_active=True, preferred_billing_day__isnull=False)
        if d7 <= 31:
            qs = qs.filter(preferred_billing_day__gte=d0, preferred_billing_day__lte=d7)
        else:
            wrap = d7 - 31
            qs = qs.filter(Q(preferred_billing_day__gte=d0) | Q(preferred_billing_day__lte=wrap))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get residents with billing day earlier this month"""
        from django.utils import timezone
        
        today = timezone.now().date()
        d0 = today.day
        overdue_residents = Resident.objects.filter(
            is_active=True,
            preferred_billing_day__lt=d0
        )
        serializer = self.get_serializer(overdue_residents, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Residents'],
        description='Get historical residents (move_out_date set). Optional filters: property, start_date, end_date (YYYY-MM-DD).',
        parameters=[
            OpenApiParameter(name='property', description='Property ID', required=False, type=OpenApiTypes.INT),
            OpenApiParameter(name='start_date', description='Move-out start date (YYYY-MM-DD)', required=False, type=OpenApiTypes.STR),
            OpenApiParameter(name='end_date', description='Move-out end date (YYYY-MM-DD)', required=False, type=OpenApiTypes.STR),
        ]
    )
    @action(detail=False, methods=['get'], url_path='historical')
    def historical(self, request):
        from datetime import datetime
        qs = Resident.objects.filter(move_out_date__isnull=False)
        prop_id = request.query_params.get('property')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if prop_id:
            qs = qs.filter(property_id=prop_id)
        if start_date:
            try:
                sd = datetime.strptime(start_date, '%Y-%m-%d').date()
                qs = qs.filter(move_out_date__gte=sd)
            except ValueError:
                return Response({'detail': 'Invalid start_date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        if end_date:
            try:
                ed = datetime.strptime(end_date, '%Y-%m-%d').date()
                qs = qs.filter(move_out_date__lte=ed)
            except ValueError:
                return Response({'detail': 'Invalid end_date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Occupancy'])
class OccupancyViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing occupancy records.
    
    - List occupancy records
    - Create new occupancy record
    - Retrieve occupancy details
    - Update occupancy information
    - Delete occupancy record
    - Get occupied beds
    - Get available beds
    """
    queryset = Occupancy.objects.all()
    serializer_class = OccupancySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'floor', 'room', 'is_occupied']
    ordering_fields = ['created_at', 'occupied_since']
    ordering = ['property', 'floor', 'room', 'bed']

    @action(detail=False, methods=['get'])
    def occupied(self, request):
        """Get all occupied beds"""
        occupied = Occupancy.objects.filter(is_occupied=True)
        serializer = self.get_serializer(occupied, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available beds"""
        available = Occupancy.objects.filter(is_occupied=False)
        serializer = self.get_serializer(available, many=True)
        return Response(serializer.data)


@extend_schema(tags=['Occupancy History'])
class OccupancyHistoryViewSet(viewsets.ModelViewSet):
    """
    API endpoints for viewing occupancy history records.
    
    - List occupancy history
    - View historical occupancy changes
    - Filter by resident, property, or action
    """
    queryset = OccupancyHistory.objects.all()
    serializer_class = OccupancyHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'resident', 'action', 'bed']
    ordering_fields = ['action_date', 'created_at']
    ordering = ['-action_date']

    def get_queryset(self):
        queryset = OccupancyHistory.objects.all()
        resident_id = self.request.query_params.get('resident_id')
        if resident_id:
            queryset = queryset.filter(resident_id=resident_id)
        return queryset


@extend_schema(tags=['Expenses'])
class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing property expenses.
    
    - List all expenses
    - Create new expense
    - Retrieve expense details
    - Update expense information
    - Delete expense
    - Get expenses grouped by category
    - Get expense summary and statistics
    """
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'category', 'payment_method']
    search_fields = ['category', 'description', 'paid_by']
    ordering_fields = ['expense_date', 'amount', 'created_at']
    ordering = ['-expense_date']

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get expenses grouped by category"""
        from django.db.models import Sum
        
        expenses_by_category = Expense.objects.values('category').annotate(
            total=Sum('amount'),
            count=Sum('id')
        )
        return Response(expenses_by_category)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get expense summary"""
        from django.db.models import Sum
        from django.utils import timezone
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        total_expenses = Expense.objects.aggregate(Sum('amount'))
        month_expenses = Expense.objects.filter(
            expense_date__gte=month_start
        ).aggregate(Sum('amount'))
        
        return Response({
            'total_expenses': total_expenses['amount__sum'] or 0,
            'this_month_expenses': month_expenses['amount__sum'] or 0,
        })


@extend_schema(tags=['Payments'])
class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing resident payments.
    
    - List all payments
    - Create new payment record
    - Retrieve payment details
    - Update payment information
    - Delete payment record
    - Get payment summary and statistics
    - Get payments by resident
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['property', 'resident', 'payment_method']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']
    permission_classes = []

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payment summary"""
        from django.db.models import Sum
        from django.utils import timezone
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        total_payments = Payment.objects.aggregate(Sum('amount'))
        month_payments = Payment.objects.filter(
            payment_date__gte=month_start
        ).aggregate(Sum('amount'))
        
        return Response({
            'total_payments': total_payments['amount__sum'] or 0,
            'this_month_payments': month_payments['amount__sum'] or 0,
        })

    @action(detail=False, methods=['get'])
    @extend_schema(
        description="Get payments aggregated for a specific resident",
        parameters=[
            OpenApiParameter(
                name='resident_id',
                description='Resident ID to aggregate payments for',
                required=True,
                type=OpenApiTypes.INT,
                location='query',
            ),
        ],
    )
    def by_resident(self, request):
        """Get payments by resident"""
        from django.db.models import Sum
        
        resident_id = request.query_params.get('resident_id')
        if resident_id:
            payments = Payment.objects.filter(resident_id=resident_id).aggregate(
                total=Sum('amount'),
                count=Sum('id')
            )
            return Response(payments)
        return Response({'error': 'resident_id parameter required'})


@extend_schema(tags=['Maintenance Requests'])
class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing maintenance requests.
    
    - List all maintenance requests
    - Create new maintenance request
    - Retrieve maintenance request details
    - Update maintenance request
    - Delete maintenance request
    - Mark request as resolved
    - Get open/pending maintenance requests
    - Filter by priority and status
    """
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'resident', 'category', 'priority', 'status']
    search_fields = ['category', 'description']
    ordering_fields = ['reported_date', 'priority', 'status', 'created_at']
    ordering = ['-reported_date']
    permission_classes = []

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a maintenance request as resolved"""
        from django.utils import timezone
        
        maintenance = self.get_object()
        maintenance.status = 'resolved'
        maintenance.resolved_date = timezone.now()
        maintenance.save()
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def open_requests(self, request):
        """Get all open maintenance requests"""
        open_requests = MaintenanceRequest.objects.filter(status='open')
        serializer = self.get_serializer(open_requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_priority(self, request):
        """Get maintenance requests grouped by priority"""
        from django.db.models import Count
        
        by_priority = MaintenanceRequest.objects.values('priority').annotate(
            count=Count('id')
        )
        return Response(by_priority)


@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing system users.
    
    - List all users
    - Create new user account
    - Retrieve user details
    - Update user information
    - Delete user account
    - Filter by property, role, or status
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'role', 'is_active']
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'created_at', 'last_login']
    ordering = ['-created_at']
    permission_classes = []


@extend_schema(tags=['Auth'])
class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints: register and login using app_user."""
    permission_classes = [AllowAny]

    @extend_schema(
        description='Create a new user',
        request=AuthRegisterSerializer,
        responses={201: AuthTokenResponseSerializer},
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        ser = AuthRegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        user = User(
            username=data['username'],
            email=data.get('email'),
            role=data.get('role') or 'staff',
            property_id=data.get('property'),
            password_hash=make_password(data['password']),
        )
        user.save()
        token = generate_jwt(user)
        return Response({'token': token, 'user': AuthUserMiniSerializer(user).data}, status=status.HTTP_201_CREATED)

    @extend_schema(
        description='Login and obtain JWT token',
        request=AuthLoginSerializer,
        responses=AuthTokenResponseSerializer,
    )
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        ser = AuthLoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        username = ser.validated_data['username']
        password = ser.validated_data['password']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        if not check_password(password, user.password_hash):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        token = generate_jwt(user)
        return Response({'token': token, 'user': AuthUserMiniSerializer(user).data})
