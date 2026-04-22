"""
Health check views for Cloud Run
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings


@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'pgadmin-api',
    }, status=200)


@require_http_methods(["GET"])
def ready_check(request):
    """Readiness check - includes database connectivity"""
    try:
        from django.db import connection
        connection.ensure_connection()
        
        # Get database configuration (for debugging)
        db_config = settings.DATABASES['default']
        
        return JsonResponse({
            'status': 'ready',
            'database': 'connected',
            'db_engine': db_config.get('ENGINE', 'unknown'),
            'db_host': db_config.get('HOST', 'unknown'),
            'db_name': db_config.get('NAME', 'unknown'),
            'db_port': db_config.get('PORT', 'unknown'),
            'db_user': db_config.get('USER', 'unknown'),
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
        }, status=503)
