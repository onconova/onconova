import logging
import json
import time
from django.utils.deprecation import MiddlewareMixin
from ninja_extra.logger import request_logger

audit_logger = logging.getLogger('audit')

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        processing_time = round((time.time() - start_time)*1000)
        
        user = getattr(request, 'user', None)
        user_id = str(user.id) if user and user.is_authenticated else 'anonymous'
        user_access_level = int(user.access_level) if user and user.is_authenticated else -1
        username = str(user.username) if user and user.is_authenticated else 'anonymous'
        audit_logger.info('', extra={
            'user_id': user_id,
            'username': username,
            'access_level': user_access_level,
            'ip': self.get_client_ip(request),
            'method': request.method,
            'duration': processing_time,
            'path': request.get_full_path(),
            'status_code': response.status_code,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:100],
            'params': self.sanitize_params(request),
        })
        return response

    def sanitize_params(self, request):
        try:
            if request.method in ['POST', 'PUT', 'PATCH']:
                body = request.body.decode('utf-8')
                data = json.loads(body)
            else:
                data = request.GET.dict()

            # Redact sensitive fields
            for key in data:
                if 'password' in key or 'token' in key or 'secret' in key:
                    data[key] = '[REDACTED]'

            return json.dumps(data, separators=(',', ':'))
        except Exception:
            return '[unreadable]'

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')