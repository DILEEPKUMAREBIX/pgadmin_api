from django.db import models

# ============================================================================
# PROPERTIES
# ============================================================================
class Property(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    floors_count = models.IntegerField(default=5)
    rooms_per_floor = models.IntegerField(default=2)
    beds_per_room = models.IntegerField(default=3)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_property'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def total_beds(self):
        return self.floors_count * self.rooms_per_floor * self.beds_per_room


# ============================================================================
# FLOORS
# ============================================================================
class Floor(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='floors')
    floor_level = models.IntegerField()
    floor_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_floor'
        unique_together = ('property', 'floor_level')
        ordering = ['property', 'floor_level']
        indexes = [
            models.Index(fields=['property', 'floor_level']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.property.name} - Floor {self.floor_level}"


# ============================================================================
# ROOMS
# ============================================================================
class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('dormitory', 'Dormitory'),
    ]

    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=50)
    room_name = models.CharField(max_length=100, null=True, blank=True)
    total_beds = models.IntegerField(default=1)
    room_type = models.CharField(max_length=50, choices=ROOM_TYPE_CHOICES, null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_room'
        unique_together = ('floor', 'room_number')
        ordering = ['floor', 'room_number']
        indexes = [
            models.Index(fields=['floor', 'room_number']),
            models.Index(fields=['property']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.floor} - Room {self.room_number}"


# ============================================================================
# BEDS
# ============================================================================
class Bed(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='beds')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=50)
    bed_name = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_bed'
        unique_together = ('room', 'bed_number')
        ordering = ['room', 'bed_number']
        indexes = [
            models.Index(fields=['room', 'bed_number']),
            models.Index(fields=['property']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.room} - Bed {self.bed_number}"


# ============================================================================
# RESIDENTS
# ============================================================================
class Resident(models.Model):
    RENT_TYPE_CHOICES = [
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('bi-weekly', 'Bi-Weekly'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='residents')
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    mobile = models.CharField(max_length=20)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    rent_type = models.CharField(max_length=20, choices=RENT_TYPE_CHOICES, default='monthly')
    joining_date = models.DateField()
    move_out_date = models.DateField(null=True, blank=True)
    next_pay_date = models.DateField()
    payment_cycle_start = models.DateField(null=True, blank=True)
    photo_url = models.URLField(null=True, blank=True)
    aadhar_url = models.URLField(null=True, blank=True)
    current_floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_residents_floor')
    current_room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_residents_room')
    current_bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_resident')
    notes = models.TextField(null=True, blank=True)
    override_comment = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_resident'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['mobile']),
            models.Index(fields=['next_pay_date']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name


# ============================================================================
# OCCUPANCY
# ============================================================================
class Occupancy(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='occupancies')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='occupancies')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='occupancies')
    bed = models.OneToOneField(Bed, on_delete=models.CASCADE, related_name='occupancy')
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True, related_name='occupancies')
    is_occupied = models.BooleanField(default=False)
    occupied_since = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_occupancy'
        verbose_name_plural = 'Occupancies'
        ordering = ['property', 'floor', 'room', 'bed']
        indexes = [
            models.Index(fields=['property', 'is_occupied']),
            models.Index(fields=['resident']),
            models.Index(fields=['is_occupied']),
        ]

    def __str__(self):
        return f"{self.bed} - {'Occupied' if self.is_occupied else 'Available'}"


# ============================================================================
# OCCUPANCY HISTORY
# ============================================================================
class OccupancyHistory(models.Model):
    ACTION_CHOICES = [
        ('occupied', 'Occupied'),
        ('freed', 'Freed'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='occupancy_histories')
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='occupancy_histories')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='occupancy_histories')
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='occupancy_histories')
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='occupancy_histories')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pg_occupancy_history'
        verbose_name_plural = 'Occupancy Histories'
        ordering = ['-action_date']
        indexes = [
            models.Index(fields=['property', 'resident']),
            models.Index(fields=['resident', '-action_date']),
            models.Index(fields=['action', '-action_date']),
        ]

    def __str__(self):
        return f"{self.resident.name} - {self.action} on {self.action_date}"


# ============================================================================
# EXPENSES
# ============================================================================
class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    expense_date = models.DateTimeField()
    paid_by = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    receipt_url = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_expense'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['property', 'category']),
            models.Index(fields=['-expense_date']),
            models.Index(fields=['amount']),
        ]

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.expense_date}"


# ============================================================================
# PAYMENTS
# ============================================================================
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='payments')
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE, related_name='payments')
    resident_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pg_payment'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['property', 'resident']),
            models.Index(fields=['resident', '-payment_date']),
            models.Index(fields=['-payment_date']),
        ]

    def __str__(self):
        return f"{self.resident_name} - {self.amount} on {self.payment_date}"


# ============================================================================
# MAINTENANCE REQUESTS
# ============================================================================
class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_requests')
    resident = models.ForeignKey(Resident, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    category = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_maintenance_request'
        ordering = ['-reported_date']
        indexes = [
            models.Index(fields=['property', 'status']),
            models.Index(fields=['priority', '-reported_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.category} - {self.get_priority_display()}"


# ============================================================================
# USERS
# ============================================================================
class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]

    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pg_user'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.username
