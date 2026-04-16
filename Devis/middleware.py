# d:/Freelance/Python_Dev/Pwa/Devis/middleware.py
# Middleware de sécurité pour limiter l'accès au panneau admin par IP.
# Réduit le risque d'accès non autorisé même si l'URL admin est découverte.
# RELEVANT FILES: Devis/settings.py, Devis/urls.py, docker-compose.yml, .env.example

from django.conf import settings
from django.http import HttpResponseForbidden


class AdminIPWhitelistMiddleware:
    """Restrict access to Django admin route to explicit client IPs."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        admin_path_prefix = '/' + settings.ADMIN_URL_PREFIX.lstrip('/')
        if request.path.startswith(admin_path_prefix):
            allowed_ips = set(settings.ADMIN_ALLOWED_IPS)
            client_ip = self._get_client_ip(request)
            if '*' not in allowed_ips and client_ip not in allowed_ips:
                return HttpResponseForbidden('Access denied from this IP.')

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
