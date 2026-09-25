import threading

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


class RequestThreadLocalMiddleware:
    """Stocke la requête HTTP courante dans un thread local.

    Permet à n'importe quel code (y compris les modèles) d'accéder à la
    requête en cours via `get_current_request()`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        try:
            response = self.get_response(request)
        finally:
            _thread_locals.request = None
        return response