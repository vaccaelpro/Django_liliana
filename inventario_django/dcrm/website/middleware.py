from django.core.cache import cache
from django.http import HttpResponse

class RateLimitMiddleware:
    """
    Capa 2 - Rate Limiting: limita intentos de login a 5 por minuto por IP.
    """
    LIMITE = 5
    VENTANA = 60  # segundos

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path in ('/Login/', '/Register/'):
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))
            if ',' in ip:
                ip = ip.split(',')[0].strip()

            cache_key = f'rate_limit_{ip}_{request.path}'
            intentos = cache.get(cache_key, 0)

            if intentos >= self.LIMITE:
                return HttpResponse(
                    "Demasiados intentos. Espera un momento antes de continuar.",
                    status=429
                )
            cache.set(cache_key, intentos + 1, self.VENTANA)

        return self.get_response(request)