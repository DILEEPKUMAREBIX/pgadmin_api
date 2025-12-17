"""
Health check views for Cloud Run
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


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
        return JsonResponse({
            'status': 'ready',
            'database': 'connected',
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e),
        }, status=503)
