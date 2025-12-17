import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgadmin_config.settings')
django.setup()

from properties.models import Property
from properties.serializers import PropertyOccupancyDetailSerializer

# Test with property ID 1
property_obj = Property.objects.get(id=1)
serializer = PropertyOccupancyDetailSerializer(property_obj)
data = serializer.data

print("="*80)
print("PROPERTY OCCUPANCY DETAIL API TEST")
print("="*80)
print(json.dumps(data, indent=2, default=str))
print("\n✅ API Response Generated Successfully!")
