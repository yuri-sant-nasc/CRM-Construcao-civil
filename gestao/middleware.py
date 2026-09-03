from .models import AuditLog


class AuditMiddleware:
    """Registra operações mutáveis sem armazenar dados pessoais da requisição."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE') and user is not None:
            # Capture real IP behind proxy
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            AuditLog.objects.create(
                user=user,
                action=request.method,
                path=request.path[:255],
                status_code=response.status_code,
                ip_address=ip,
            )
        return response
