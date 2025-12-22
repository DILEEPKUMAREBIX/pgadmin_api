from rest_framework import serializers
from django.db.models import Sum, Count
from .models import (
    Property, Floor, Room, Bed, Resident, Occupancy, OccupancyHistory,
    Expense, Payment, MaintenanceRequest, User
)


class PropertySerializer(serializers.ModelSerializer):
    total_beds = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'address', 'city', 'state', 'zip_code',
            'floors_count', 'rooms_per_floor', 'beds_per_room',
            'total_beds', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_beds(self, obj):
        return obj.total_beds


class FloorSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Floor
        fields = [
            'id', 'property', 'property_name', 'floor_level', 'floor_name',
            'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoomSerializer(serializers.ModelSerializer):
    floor_name = serializers.CharField(source='floor.floor_name', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Room
        fields = [
            'id', 'floor', 'floor_name', 'property', 'property_name',
            'room_number', 'room_name', 'total_beds', 'room_type',
            'capacity', 'description', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BedSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    floor_level = serializers.IntegerField(source='floor.floor_level', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Bed
        fields = [
            'id', 'room', 'room_number', 'floor', 'floor_level',
            'property', 'property_name', 'bed_number', 'bed_name',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResidentSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    name = serializers.CharField(read_only=True)
    # Write-only inputs for assigning occupancy on create
    floor_id = serializers.IntegerField(write_only=True, required=False)
    room_id = serializers.IntegerField(write_only=True, required=False)
    bed_id = serializers.IntegerField(write_only=True, required=False)
    # Derive current location from active Occupancy to avoid model field coupling
    current_floor = serializers.SerializerMethodField()
    current_floor_number = serializers.SerializerMethodField()
    current_room = serializers.SerializerMethodField()
    current_room_number = serializers.SerializerMethodField()
    current_bed = serializers.SerializerMethodField()
    current_bed_number = serializers.SerializerMethodField()
    # Payments summary for resident
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Resident
        fields = [
            'id', 'property', 'property_name', 'first_name', 'last_name', 'name',
            'gender', 'email', 'mobile', 'dob', 'address', 'rent', 'rent_type',
            'joining_date', 'move_out_date', 'preferred_billing_day',
            'photo_url', 'aadhar_url', 'current_floor', 'current_floor_number',
            'current_room', 'current_room_number', 'current_bed', 'current_bed_number',
            'floor_id', 'room_id', 'bed_id',
            'payments',
            'notes', 'override_comment', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'name']

    def _get_active_occupancy(self, obj):
        return Occupancy.objects.select_related('floor', 'room', 'bed').filter(resident=obj, is_occupied=True).first()

    def get_current_floor(self, obj):
        occ = self._get_active_occupancy(obj)
        return occ.floor.id if occ and occ.floor else None

    def get_current_floor_number(self, obj):
        occ = self._get_active_occupancy(obj)
        return occ.floor.floor_level if occ and occ.floor else None

    def get_current_room(self, obj):
        occ = self._get_active_occupancy(obj)
        return occ.room.id if occ and occ.room else None

    def get_current_room_number(self, obj):
        occ = self._get_active_occupancy(obj)
        return occ.room.room_number if occ and occ.room else None

    def get_current_bed(self, obj):
        occ = self._get_active_occupancy(obj)
        return occ.bed.id if occ and occ.bed else None

    def get_current_bed_number(self, obj):
        occ = self._get_active_occupancy(obj)
        return occ.bed.bed_number if occ and occ.bed else None

    def get_payments(self, obj):
        qs = Payment.objects.filter(resident=obj).order_by('-payment_date')
        return PaymentSummarySerializer(qs, many=True).data

    def validate(self, attrs):
        # On create, require floor_id, room_id, bed_id; on update, allow missing
        if self.instance is None:
            missing = [k for k in ['floor_id', 'room_id', 'bed_id'] if attrs.get(k) in (None, '')]
            if missing:
                raise serializers.ValidationError({m: 'This field is required on create.' for m in missing})
            # Validate existence and relationships
            try:
                floor = Floor.objects.get(id=attrs['floor_id'])
                room = Room.objects.get(id=attrs['room_id'])
                bed = Bed.objects.get(id=attrs['bed_id'])
            except (Floor.DoesNotExist, Room.DoesNotExist, Bed.DoesNotExist):
                raise serializers.ValidationError('Invalid floor_id/room_id/bed_id.')
            if room.floor_id != floor.id:
                raise serializers.ValidationError('room_id does not belong to floor_id.')
            if bed.room_id != room.id:
                raise serializers.ValidationError('bed_id does not belong to room_id.')
            # Property consistency (property must match floor/room/bed property)
            prop = attrs.get('property')
            if prop:
                if floor.property_id != prop.id or room.property_id != prop.id or bed.property_id != prop.id:
                    raise serializers.ValidationError('floor/room/bed must belong to the same property as resident.')
            # Bed availability
            occ = Occupancy.objects.filter(bed_id=bed.id).first()
            if occ and occ.is_occupied:
                raise serializers.ValidationError('Selected bed is already occupied.')
        return attrs

    def create(self, validated_data):
        floor_id = validated_data.pop('floor_id', None)
        room_id = validated_data.pop('room_id', None)
        bed_id = validated_data.pop('bed_id', None)
        resident = super().create(validated_data)
        # Assign occupancy if IDs provided
        if floor_id and room_id and bed_id:
            floor = Floor.objects.get(id=floor_id)
            room = Room.objects.get(id=room_id)
            bed = Bed.objects.get(id=bed_id)
            # Final safety: ensure all belong to resident.property
            if not (floor.property_id == resident.property_id == room.property_id == bed.property_id):
                raise serializers.ValidationError('floor/room/bed must belong to resident.property')
            from django.utils import timezone
            Occupancy.objects.update_or_create(
                bed=bed,
                defaults={
                    'property': resident.property,
                    'floor': floor,
                    'room': room,
                    'resident': resident,
                    'is_occupied': True,
                    'occupied_since': timezone.now().date(),
                }
            )
        return resident


class OccupancySerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    floor_level = serializers.IntegerField(source='floor.floor_level', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    bed_number = serializers.CharField(source='bed.bed_number', read_only=True)
    resident_name = serializers.CharField(source='resident.name', read_only=True)

    class Meta:
        model = Occupancy
        fields = [
            'id', 'property', 'property_name', 'floor', 'floor_level',
            'room', 'room_number', 'bed', 'bed_number', 'resident',
            'resident_name', 'is_occupied', 'occupied_since',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OccupancyHistorySerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    floor_level = serializers.IntegerField(source='floor.floor_level', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    bed_number = serializers.CharField(source='bed.bed_number', read_only=True)
    resident_name = serializers.CharField(source='resident.name', read_only=True)

    class Meta:
        model = OccupancyHistory
        fields = [
            'id', 'property', 'property_name', 'floor', 'floor_level',
            'room', 'room_number', 'bed', 'bed_number', 'resident',
            'resident_name', 'action', 'action_date', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'action_date']


class ExpenseSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'property', 'property_name', 'amount', 'category',
            'description', 'expense_date', 'paid_by', 'payment_method',
            'receipt_url', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    resident_detail = ResidentSerializer(source='resident', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'property', 'property_name', 'resident', 'resident_name',
            'resident_detail', 'amount', 'payment_date', 'payment_method',
            'reference_number', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'payment_date']

class PaymentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'amount', 'payment_date', 'payment_method', 'reference_number', 'notes'
        ]


# ============================================================================
# AUTH SERIALIZERS (for Swagger docs and validation)
# ============================================================================
class AuthRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    role = serializers.ChoiceField(choices=[c[0] for c in User.ROLE_CHOICES], default='staff')
    property = serializers.IntegerField(required=False, allow_null=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value


class AuthLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AuthUserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'property']


class AuthTokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = AuthUserMiniSerializer()


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True)
    resident_name = serializers.CharField(source='resident.name', read_only=True, allow_null=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'property', 'property_name', 'resident', 'resident_name',
            'category', 'description', 'priority', 'status', 'reported_date',
            'resolved_date', 'estimated_cost', 'actual_cost', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reported_date']


class UserSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'property', 'property_name', 'username', 'email', 'role',
            'is_active', 'last_login', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']
        extra_kwargs = {
            'password_hash': {'write_only': True}
        }


# ============================================================================
# CONSOLIDATED OCCUPANCY VIEW SERIALIZERS
# ============================================================================
class BedOccupancySerializer(serializers.Serializer):
    """Serialize bed with occupancy status"""
    bed_id = serializers.IntegerField(source='id')
    bed_number = serializers.CharField()
    bed_name = serializers.CharField()
    is_occupied = serializers.SerializerMethodField()
    resident_name = serializers.SerializerMethodField()
    resident_id = serializers.SerializerMethodField()

    def get_is_occupied(self, obj):
        """Check if bed is occupied"""
        occupancy = Occupancy.objects.filter(bed=obj, is_occupied=True).first()
        return occupancy is not None

    def get_resident_name(self, obj):
        """Get resident name if bed is occupied"""
        occupancy = Occupancy.objects.filter(bed=obj, is_occupied=True).first()
        return occupancy.resident.name if occupancy and occupancy.resident else None

    def get_resident_id(self, obj):
        """Get resident ID if bed is occupied"""
        occupancy = Occupancy.objects.filter(bed=obj, is_occupied=True).first()
        return occupancy.resident.id if occupancy and occupancy.resident else None


class RoomOccupancySerializer(serializers.Serializer):
    """Serialize room with bed occupancy details"""
    room_id = serializers.IntegerField(source='id')
    room_number = serializers.CharField()
    room_name = serializers.CharField()
    room_type = serializers.CharField()
    total_beds = serializers.IntegerField()
    beds = serializers.SerializerMethodField()
    occupied_count = serializers.SerializerMethodField()
    available_count = serializers.SerializerMethodField()

    def get_beds(self, obj):
        """Get all beds in the room with occupancy status"""
        beds = obj.beds.all()
        return BedOccupancySerializer(beds, many=True).data

    def get_occupied_count(self, obj):
        """Count occupied beds in room"""
        return Occupancy.objects.filter(room=obj, is_occupied=True).count()

    def get_available_count(self, obj):
        """Count available beds in room"""
        return Occupancy.objects.filter(room=obj, is_occupied=False).count()


class FloorOccupancySerializer(serializers.Serializer):
    """Serialize floor with room and occupancy details"""
    floor_id = serializers.IntegerField(source='id')
    floor_level = serializers.IntegerField()
    floor_name = serializers.CharField()
    rooms = serializers.SerializerMethodField()
    total_beds = serializers.SerializerMethodField()
    occupied_beds = serializers.SerializerMethodField()
    available_beds = serializers.SerializerMethodField()

    def get_rooms(self, obj):
        """Get all rooms on the floor with occupancy details"""
        rooms = obj.rooms.all()
        return RoomOccupancySerializer(rooms, many=True).data

    def get_total_beds(self, obj):
        """Total beds on floor"""
        return obj.rooms.aggregate(total=Sum('total_beds'))['total'] or 0

    def get_occupied_beds(self, obj):
        """Count occupied beds on floor"""
        return Occupancy.objects.filter(floor=obj, is_occupied=True).count()

    def get_available_beds(self, obj):
        """Count available beds on floor"""
        return Occupancy.objects.filter(floor=obj, is_occupied=False).count()


class PropertyOccupancyDetailSerializer(serializers.Serializer):
    """Serialize complete property with floor, room, and occupancy details"""
    property_id = serializers.IntegerField(source='id')
    property_name = serializers.CharField(source='name')
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    zip_code = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    
    # Property level statistics
    total_floors = serializers.SerializerMethodField()
    total_rooms = serializers.SerializerMethodField()
    total_beds = serializers.SerializerMethodField()
    occupied_beds = serializers.SerializerMethodField()
    available_beds = serializers.SerializerMethodField()
    occupancy_percentage = serializers.SerializerMethodField()
    
    # Detailed floor information
    floors = serializers.SerializerMethodField()

    def get_total_floors(self, obj):
        """Total number of floors"""
        return obj.floors.count()

    def get_total_rooms(self, obj):
        """Total number of rooms"""
        return obj.rooms.count()

    def get_total_beds(self, obj):
        """Total beds in property"""
        return obj.total_beds

    def get_occupied_beds(self, obj):
        """Total occupied beds in property"""
        return Occupancy.objects.filter(property=obj, is_occupied=True).count()

    def get_available_beds(self, obj):
        """Total available beds in property"""
        return Occupancy.objects.filter(property=obj, is_occupied=False).count()

    def get_occupancy_percentage(self, obj):
        """Calculate occupancy percentage"""
        total = obj.total_beds
        if total == 0:
            return 0
        occupied = self.get_occupied_beds(obj)
        return round((occupied / total) * 100, 2)

    def get_floors(self, obj):
        """Get all floors with detailed room and occupancy info"""
        floors = obj.floors.all().order_by('floor_level')
        return FloorOccupancySerializer(floors, many=True).data
