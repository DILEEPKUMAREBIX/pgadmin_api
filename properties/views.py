from rest_framework import viewsets, filters, status, serializers
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password, check_password
from core.auth import generate_jwt
from django.conf import settings
import logging
import mimetypes
from urllib.parse import urlparse
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
    UserSerializer, PropertyOccupancyDetailSerializer,
    PropertySetupRequestSerializer, PropertySetupResponseSerializer,
    ResidentMoveSerializer
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
        tags=['Properties'],
        description='Configure property structure in one call: create floors, rooms per floor, and beds per room. Optionally provide names.',
        request=PropertySetupRequestSerializer,
        responses=PropertySetupResponseSerializer,
    )
    @action(detail=True, methods=['post'], url_path='setup-structure')
    def setup_structure(self, request, pk=None):
        """Create floors, rooms, and beds for a property in a single request.

        Payload:
        - floors_count: int
        - rooms_per_floor: int
        - beds_per_room: int
        - floor_names: [str] (optional, length = floors_count)
        - room_numbers: { '<floor_level>': [str, ...] } (optional)
        - bed_numbers: { '<floor_level>': { '<room_number>': [str, ...] } } (optional)
        - reset: bool (optional) — if true, clears existing floors/rooms/beds first
        """
        property_obj = self.get_object()
        input_ser = PropertySetupRequestSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        data = input_ser.validated_data

        # Optionally update property details
        prop_update_fields = []
        for fld in ['name', 'address', 'city', 'state', 'zip_code']:
            if fld in data and data.get(fld) is not None:
                setattr(property_obj, fld, data.get(fld))
                prop_update_fields.append(fld)
        if prop_update_fields:
            try:
                property_obj.save(update_fields=prop_update_fields)
            except IntegrityError:
                return Response({'detail': 'Property name must be unique.'}, status=status.HTTP_400_BAD_REQUEST)

        floors_count = data.get('floors_count')
        rooms_per_floor = data.get('rooms_per_floor')  # default when room_numbers absent
        beds_per_room = data.get('beds_per_room')      # default when bed_numbers absent
        floor_names = data.get('floor_names') or []
        room_numbers_map = data.get('room_numbers') or {}
        bed_numbers_map = data.get('bed_numbers') or {}
        reset = data.get('reset', False)

        created_floors = 0
        created_rooms = 0
        created_beds = 0

        with transaction.atomic():
            if reset:
                # Cascade deletes rooms/beds/occupancies via FK
                property_obj.floors.all().delete()

            # If not resetting, ensure no conflict with existing structure
            elif property_obj.floors.exists():
                return Response({'detail': 'Property already has floors. Pass reset=true to reconfigure.'}, status=status.HTTP_400_BAD_REQUEST)

            # Determine floors to create
            floor_levels = list(range(1, (floors_count or 0) + 1))
            if not floor_levels:
                # Fallback: infer from provided maps
                keys = set()
                for k in (room_numbers_map.keys() | bed_numbers_map.keys()):
                    try:
                        keys.add(int(k))
                    except Exception:
                        pass
                floor_levels = sorted(keys)
            if not floor_levels:
                return Response({'detail': 'No floors defined (provide floors_count or room_numbers/bed_numbers keys).'}, status=status.HTTP_400_BAD_REQUEST)

            # Create floors → rooms → beds (+ occupancy)
            for level in floor_levels:
                fname = floor_names[level - 1] if level - 1 < len(floor_names) else f'Floor {level}'
                floor = Floor.objects.create(property=property_obj, floor_level=level, floor_name=fname)
                created_floors += 1

                # Determine room numbers for this floor
                rn_list = room_numbers_map.get(str(level)) or room_numbers_map.get(level) or []

                # If explicit room list provided, use it; else fall back to default count
                if rn_list:
                    room_iter = [(i + 1, rn_list[i]) for i in range(len(rn_list))]
                else:
                    if not rooms_per_floor:
                        return Response({'detail': f'rooms_per_floor missing and no room_numbers provided for floor {level}.'}, status=status.HTTP_400_BAD_REQUEST)
                    room_iter = [(r_idx, f'{level:02d}{r_idx:02d}') for r_idx in range(1, rooms_per_floor + 1)]

                bn_floor = bed_numbers_map.get(str(level)) or bed_numbers_map.get(level) or {}

                for r_idx, room_number in room_iter:
                    # Beds per room: explicit list overrides default
                    bn_list = bn_floor.get(room_number) or []

                    # Determine bed iteration
                    if bn_list:
                        bed_iter = [(i + 1, bn_list[i]) for i in range(len(bn_list))]
                        bed_count_for_room = len(bn_list)
                    else:
                        if not beds_per_room:
                            return Response({'detail': f'beds_per_room missing and no bed_numbers provided for floor {level} room {room_number}.'}, status=status.HTTP_400_BAD_REQUEST)
                        bed_iter = [(b_idx, (chr(64 + b_idx) if b_idx <= 26 else str(b_idx))) for b_idx in range(1, beds_per_room + 1)]
                        bed_count_for_room = beds_per_room

                    room = Room.objects.create(
                        floor=floor,
                        property=property_obj,
                        room_number=room_number,
                        total_beds=bed_count_for_room,
                    )
                    created_rooms += 1

                    for b_idx, bed_number in bed_iter:
                        bed = Bed.objects.create(
                            room=room,
                            floor=floor,
                            property=property_obj,
                            bed_number=bed_number,
                            bed_name=bed_number,
                        )
                        created_beds += 1

                        # Initialize occupancy as available
                        Occupancy.objects.create(
                            property=property_obj,
                            floor=floor,
                            room=room,
                            bed=bed,
                            is_occupied=False,
                        )

        # Update property numeric fields to reflect configured structure (optional)
        if floors_count:
            property_obj.floors_count = floors_count
        if rooms_per_floor:
            property_obj.rooms_per_floor = rooms_per_floor
        if beds_per_room:
            property_obj.beds_per_room = beds_per_room
        property_obj.save(update_fields=['floors_count', 'rooms_per_floor', 'beds_per_room'])

        out = PropertySetupResponseSerializer({
            'property_id': property_obj.id,
            'created_floors': created_floors,
            'created_rooms': created_rooms,
            'created_beds': created_beds,
        })
        return Response(out.data, status=status.HTTP_201_CREATED)

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
        from decimal import Decimal
        from .payment_utils import calculate_due_amount, is_overdue, get_overdue_amount
        import calendar

        property_obj = self.get_object()
        today = timezone.now().date()

        def days_in_month(y: int, m: int):
            return calendar.monthrange(y, m)[1]

        # Get all active residents with active occupancy (not moved out)
        residents = Resident.objects.filter(
            property=property_obj,
            is_active=True,
            move_out_date__isnull=True,
        )

        overdue_details = []  # Residents with overdue payments
        due_details = []      # Residents with due or upcoming due payments (not yet overdue)
        overdue_total_amount = Decimal(0)
        due_total_amount = Decimal(0)

        for resident in residents:
            if not resident.is_active or not resident.joining_date:
                continue
                
            due_amount = calculate_due_amount(resident, today)
            
            # Skip residents with no due amount at all
            if due_amount <= 0:
                continue
            
            resident_data = ResidentSerializer(resident).data
            resident_data['due_amount'] = str(due_amount.quantize(Decimal('0.01')))
            
            # Check if overdue
            if is_overdue(resident, today):
                # Overdue: has due amount and payment date has passed
                overdue_details.append(resident_data)
                overdue_total_amount += due_amount
            else:
                # Not yet overdue - check if due soon or upcoming
                # For DAILY residents: due if 0+ days have passed (same day onwards)
                # For WEEKLY residents: due if approaching end of week
                # For MONTHLY residents: due if payment date approaching OR has arrears
                
                should_add_to_due = False
                add_due_amount = due_amount if due_amount > 0 else Decimal(0)
                
                if resident.rent_type == 'daily':
                    # Daily: show as DUE if joined today or earlier (any accumulated rent)
                    if resident.joining_date and resident.joining_date <= today:
                        should_add_to_due = True
                        add_due_amount = due_amount
                
                elif resident.rent_type == 'weekly':
                    # Weekly: show as DUE if approaching a week (5+ days in)
                    if resident.joining_date:
                        days_since_joining = (today - resident.joining_date).days
                        week_position = days_since_joining % 7
                        # Show as due if in last 2 days of week (days 5-6 out of 0-6)
                        if week_position >= 5:
                            should_add_to_due = True
                            add_due_amount = due_amount
                
                elif resident.rent_type == 'bi-weekly':
                    # Bi-weekly: show as DUE if approaching payment (11+ days in)
                    if resident.joining_date:
                        days_since_joining = (today - resident.joining_date).days
                        biweek_position = days_since_joining % 14
                        # Show as due if in last 3 days of bi-weekly period
                        if biweek_position >= 11:
                            should_add_to_due = True
                            add_due_amount = due_amount
                
                elif resident.rent_type == 'monthly':
                    # Monthly: show as DUE if:
                    # 1. Next billing date is approaching (within 5 days), OR
                    # 2. Has arrears (even if no rent accrued yet)
                    from .payment_utils import next_billing_date
                    
                    has_arrears = Decimal(resident.arrears or 0) > 0
                    next_bill = next_billing_date(resident, today)
                    
                    if next_bill:
                        delta_days = (next_bill - today).days
                        # Show if next billing date is within 5 days forward or 1 day past
                        is_billing_soon = -1 <= delta_days <= 5
                    else:
                        is_billing_soon = False
                    
                    # Show as DUE if billing is approaching OR has arrears
                    if is_billing_soon or has_arrears:
                        should_add_to_due = True
                        add_due_amount = due_amount
                
                if should_add_to_due:
                    due_details.append(resident_data)
                    due_total_amount += add_due_amount

        # Beds summary
        occupied_beds = Occupancy.objects.filter(property=property_obj, is_occupied=True).count()
        # 'available' should reflect total beds in the property
        available_beds = Bed.objects.filter(room__floor__property=property_obj).count()

        return Response({
            'property': {
                'id': property_obj.id,
                'name': property_obj.name,
            },
            'occupied_beds': occupied_beds,
            'available_beds': available_beds,
            'overdue': {
                'count': len(overdue_details),
                'total_amount': str(overdue_total_amount.quantize(Decimal('0.01'))),
                'details': overdue_details,
            },
            'due': {
                'count': len(due_details),
                'total_amount': str(due_total_amount.quantize(Decimal('0.01'))),
                'details': due_details,
            },
        })


    @extend_schema(tags=['Finance'], description='Financial summary for the last 5 years with monthly income (payments) and expenses. Returns per-year totals and top spending categories.')
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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property', 'is_active', 'rent_type']
    search_fields = ['first_name', 'last_name', 'email', 'mobile']
    ordering_fields = ['first_name', 'last_name', 'joining_date', 'preferred_billing_day', 'created_at']
    ordering = ['-created_at']
    logger = logging.getLogger(__name__)

    def _upload_to_gcs(self, resident: Resident, file_obj, kind: str):
        """Upload a file object to GCS and return the public URL."""
        bucket_name = settings.GCS_BUCKET
        if not bucket_name or not file_obj:
            self.logger.warning("GCS upload skipped: bucket=%s file_present=%s kind=%s", bucket_name, bool(file_obj), kind)
            return None
        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            filename = getattr(file_obj, 'name', None) or f'{kind}.bin'
            prefix = settings.GCS_UPLOAD_PREFIX or 'properties'
            object_name = f"{prefix}/{resident.property_id}/residents/{resident.id}/{kind}/{filename}"
            blob = bucket.blob(object_name)
            content_type = getattr(file_obj, 'content_type', None)
            try:
                # Ensure stream at beginning; google client can rewind too
                if hasattr(file_obj, 'seek'):
                    file_obj.seek(0)
                blob.upload_from_file(getattr(file_obj, 'file', file_obj), content_type=content_type, rewind=True)
            except Exception as e:
                self.logger.exception("GCS upload error for kind=%s object=%s: %s", kind, object_name, e)
                return None
            url = f"https://storage.googleapis.com/{bucket_name}/{object_name}"
            self.logger.info("GCS upload success: kind=%s url=%s", kind, url)
            return url
        except Exception as e:
            self.logger.exception("GCS client/bucket error: %s", e)
            return None

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

    @extend_schema(
        description='Create resident and optionally upload photo/aadhar via multipart/form-data (fields: photo, aadhar).',
        responses=ResidentSerializer,
    )
    def create(self, request, *args, **kwargs):
        """Create resident and handle optional file uploads to GCS in one step."""
        self.logger.info("Resident create: content_type=%s", getattr(request, 'content_type', None))
        self.logger.debug("Resident create: data_keys=%s file_keys=%s", list(getattr(request, 'data', {}).keys()), list(getattr(request, 'FILES', {}).keys()))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.logger.info("Resident create: serializer valid for first_name=%s", serializer.validated_data.get('first_name'))
        resident = serializer.save()
        self.logger.info("Resident create: resident saved id=%s property_id=%s", resident.id, resident.property_id)
        # Handle optional file uploads
        photo_file = request.FILES.get('photo')
        aadhar_file = request.FILES.get('aadhar')
        self.logger.info("Resident create: files present photo=%s aadhar=%s", bool(photo_file), bool(aadhar_file))
        updated_fields = []
        if photo_file:
            self.logger.info("Resident create: uploading photo name=%s size=%s ctype=%s", getattr(photo_file, 'name', None), getattr(photo_file, 'size', None), getattr(photo_file, 'content_type', None))
            url = self._upload_to_gcs(resident, photo_file, 'photo')
            if url:
                resident.photo_url = url
                updated_fields.append('photo_url')
        if aadhar_file:
            self.logger.info("Resident create: uploading aadhar name=%s size=%s ctype=%s", getattr(aadhar_file, 'name', None), getattr(aadhar_file, 'size', None), getattr(aadhar_file, 'content_type', None))
            url = self._upload_to_gcs(resident, aadhar_file, 'aadhar')
            if url:
                resident.aadhar_url = url
                updated_fields.append('aadhar_url')
        if updated_fields:
            resident.save(update_fields=updated_fields)
            self.logger.info("Resident create: saved media URLs photo_url=%s aadhar_url=%s", resident.photo_url, resident.aadhar_url)
        out = self.get_serializer(resident)
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        description='Proxy private media from GCS for a resident. Kind can be "photo" or "aadhar". Streams bytes with correct Content-Type.',
        parameters=[
            OpenApiParameter(name='kind', description='Media kind: photo or aadhar', required=True, type=OpenApiTypes.STR),
        ],
    )
    @action(detail=True, methods=['get'], url_path='media/(?P<kind>[^/.]+)')
    def media(self, request, pk=None, kind=None):
        """Stream resident media securely from GCS without exposing public bucket access."""
        resident = self.get_object()
        if kind not in ('photo', 'aadhar'):
            return Response({'detail': 'Invalid kind. Use photo or aadhar.'}, status=status.HTTP_400_BAD_REQUEST)
        url = resident.photo_url if kind == 'photo' else resident.aadhar_url
        if not url:
            return Response({'detail': 'Media not available for resident.'}, status=status.HTTP_404_NOT_FOUND)

        bucket_name = settings.GCS_BUCKET
        if not bucket_name:
            self.logger.error('Media proxy: GCS_BUCKET not configured')
            return Response({'detail': 'Storage not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            from google.cloud import storage
            parsed = urlparse(url)
            parts = parsed.path.strip('/').split('/')
            # Expect path like /<bucket>/<object_name>
            object_name = None
            if parts and parts[0] == bucket_name:
                object_name = '/'.join(parts[1:])
            else:
                # Fallback: if a full URL is not using storage.googleapis.com format, try to use entire path
                # e.g., if photo_url stored as just object path
                object_name = '/'.join(parts)

            if not object_name:
                self.logger.error('Media proxy: could not parse object name from url=%s', url)
                return Response({'detail': 'Invalid media url'}, status=status.HTTP_400_BAD_REQUEST)

            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            if not blob.exists():
                self.logger.warning('Media proxy: blob not found bucket=%s object=%s', bucket_name, object_name)
                return Response({'detail': 'Media not found'}, status=status.HTTP_404_NOT_FOUND)
            # Load metadata for content_type
            blob.reload()
            content_type = blob.content_type or mimetypes.guess_type(object_name)[0] or 'application/octet-stream'
            data = blob.download_as_bytes()
            from django.http import HttpResponse
            resp = HttpResponse(data, content_type=content_type)
            resp['Cache-Control'] = 'private, max-age=300'
            # Inline display for common types
            filename = object_name.rsplit('/', 1)[-1]
            resp['Content-Disposition'] = 'inline; filename="%s"' % filename
            return resp
        except Exception as e:
            self.logger.exception('Media proxy error kind=%s resident_id=%s: %s', kind, resident.id, e)
            return Response({'detail': 'Media fetch error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        description='Checkout due summary for a resident. Includes detailed formula and payment breakdown used to compute remaining due.',
        parameters=[
            OpenApiParameter(
                name='checkout_date',
                description='Optional checkout date in YYYY-MM-DD. Defaults to today.',
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name='monthly_option',
                description='Monthly checkout strategy: rounded_month (default) or prorated_days.',
                required=False,
                type=OpenApiTypes.STR,
            ),
        ],
        responses={200: OpenApiTypes.OBJECT},
    )
    @action(detail=True, methods=['get'], url_path='checkout')
    def checkout(self, request, pk=None):
        """Calculate resident checkout settlement with transparent due breakdown."""
        from datetime import datetime
        from django.utils import timezone
        from .payment_utils import calculate_checkout_breakdown

        resident = self.get_object()
        checkout_date_str = request.query_params.get('checkout_date')
        monthly_option = (request.query_params.get('monthly_option') or 'rounded_month').strip().lower()

        if monthly_option not in ('rounded_month', 'prorated_days'):
            return Response(
                {'detail': 'Invalid monthly_option. Use rounded_month or prorated_days.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if checkout_date_str:
            try:
                checkout_date = datetime.strptime(checkout_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'Invalid checkout_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            checkout_date = timezone.now().date()

        data = calculate_checkout_breakdown(resident, checkout_date, monthly_option=monthly_option)
        return Response(data)

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

    @extend_schema(
        tags=['Residents'],
        description='Move a resident to a new bed. This frees the old bed and occupies the new one.',
        request=ResidentMoveSerializer,
        responses=ResidentSerializer,
    )
    @action(detail=True, methods=['post'], url_path='move')
    def move(self, request, pk=None):
        resident = self.get_object()
        ser = ResidentMoveSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        new_bed_id = ser.validated_data['new_bed_id']

        try:
            new_bed = Bed.objects.select_related('room', 'floor', 'property').get(id=new_bed_id)
        except Bed.DoesNotExist:
            return Response({'detail': 'Invalid new_bed_id.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the new bed belongs to the same property
        if new_bed.property_id != resident.property_id:
            return Response({'detail': 'New bed must belong to the same property as the resident.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Check if new bed is already occupied
            new_occupancy, created = Occupancy.objects.get_or_create(
                bed=new_bed,
                defaults={
                    'property': new_bed.property,
                    'floor': new_bed.floor,
                    'room': new_bed.room,
                    'is_occupied': False
                }
            )

            if new_occupancy.is_occupied:
                return Response({'detail': 'The selected bed is already occupied.'}, status=status.HTTP_400_BAD_REQUEST)

            # Find current occupancy
            current_occupancy = Occupancy.objects.filter(resident=resident, is_occupied=True).first()
            if not current_occupancy:
                return Response({'detail': 'Resident does not have an active occupancy to move from.'}, status=status.HTTP_400_BAD_REQUEST)

            old_bed = current_occupancy.bed

            # Free the old bed
            current_occupancy.is_occupied = False
            current_occupancy.resident = None
            current_occupancy.save(update_fields=['is_occupied', 'resident', 'updated_at'])

            # Occupy the new bed
            from django.utils import timezone
            new_occupancy.is_occupied = True
            new_occupancy.resident = resident
            new_occupancy.occupied_since = timezone.now().date()
            new_occupancy.save(update_fields=['is_occupied', 'resident', 'occupied_since', 'updated_at'])

            # Log history
            OccupancyHistory.objects.create(
                property=resident.property,
                floor=old_bed.floor,
                room=old_bed.room,
                bed=old_bed,
                resident=resident,
                action='freed',
                notes=f'Moved to Room {new_bed.room.room_number}, Bed {new_bed.bed_number}'
            )

            OccupancyHistory.objects.create(
                property=resident.property,
                floor=new_bed.floor,
                room=new_bed.room,
                bed=new_bed,
                resident=resident,
                action='occupied',
                notes=f'Moved from Room {old_bed.room.room_number}, Bed {old_bed.bed_number}'
            )

        # Refresh resident and return
        resident.refresh_from_db()
        return Response(self.get_serializer(resident).data)


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
        auth=[],
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
        auth=[],
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
