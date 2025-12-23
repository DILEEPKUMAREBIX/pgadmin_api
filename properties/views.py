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

    @extend_schema(tags=['Home'], description='Home screen summary for a property')
    @action(detail=True, methods=['get'])
    def home_summary(self, request, pk=None):
        from django.utils import timezone
        from django.db.models import Sum
        property_obj = self.get_object()
        today = timezone.now().date()
        d0 = today.day
        d5 = d0 + 5

        base_residents = Resident.objects.filter(
            property=property_obj,
            is_active=True,
            move_out_date__isnull=True,
            preferred_billing_day__isnull=False,
        )

        # Overdue: billing day earlier this month
        overdue_qs = base_residents.filter(preferred_billing_day__lt=d0)

        # Due soon within 5 days (wrap at month end)
        if d5 <= 31:
            due_soon_qs = base_residents.filter(preferred_billing_day__gte=d0, preferred_billing_day__lte=d5)
        else:
            wrap = d5 - 31
            due_soon_qs = base_residents.filter(Q(preferred_billing_day__gte=d0) | Q(preferred_billing_day__lte=wrap))

        overdue_total = overdue_qs.aggregate(total=Sum('rent'))['total'] or 0
        due_soon_total = due_soon_qs.aggregate(total=Sum('rent'))['total'] or 0

        # Beds summary
        occupied_beds = Occupancy.objects.filter(property=property_obj, is_occupied=True).count()
        available_beds = Occupancy.objects.filter(property=property_obj, is_occupied=False).count()

        # Expenses
        year_start = today.replace(month=1, day=1)
        month_start = today.replace(day=1)
        expenses_year = Expense.objects.filter(expense_date__date__gte=year_start, expense_date__date__lte=today).aggregate(Sum('amount'))
        expenses_month = Expense.objects.filter(expense_date__date__gte=month_start, expense_date__date__lte=today).aggregate(Sum('amount'))

        # Serialize resident details (mini)
        overdue_data = ResidentSerializer(overdue_qs, many=True).data
        due_soon_data = ResidentSerializer(due_soon_qs, many=True).data

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
                'count': overdue_qs.count(),
                'total_amount': float(overdue_total),
                'residents': overdue_data,
            },
            'due_soon': {
                'count': due_soon_qs.count(),
                'total_amount': float(due_soon_total),
                'residents': due_soon_data,
            },
            'expenses': {
                'year_total': float(expenses_year['amount__sum'] or 0),
                'month_total': float(expenses_month['amount__sum'] or 0),
            }
        })


@extend_schema(tags=['Floors'])
class FloorViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing floors within properties.
    
    - List floors by property
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
