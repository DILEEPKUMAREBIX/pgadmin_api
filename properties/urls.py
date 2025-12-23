from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet, FloorViewSet, RoomViewSet, BedViewSet,
    ResidentViewSet, OccupancyViewSet, OccupancyHistoryViewSet,
    ExpenseViewSet, PaymentViewSet, MaintenanceRequestViewSet,
    UserViewSet, AuthViewSet
)

router = DefaultRouter()
# Accept both with and without trailing slash (avoid 405 on POST without slash)
router.trailing_slash = '/?'
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'floors', FloorViewSet, basename='floor')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'beds', BedViewSet, basename='bed')
router.register(r'residents', ResidentViewSet, basename='resident')
router.register(r'occupancy', OccupancyViewSet, basename='occupancy')
router.register(r'occupancy-history', OccupancyHistoryViewSet, basename='occupancy-history')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'maintenance-requests', MaintenanceRequestViewSet, basename='maintenance-request')
router.register(r'users', UserViewSet, basename='user')
router.register(r'auth', AuthViewSet, basename='auth')

app_name = 'properties'

urlpatterns = [
    path('', include(router.urls)),
]
