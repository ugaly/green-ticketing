from django.conf import settings
from django.http import HttpResponse


class SimpleCORSMiddleware:
    """
    Minimal CORS middleware to allow a React/Next.js frontend on localhost:3000.

    We avoid adding extra dependencies (like django-cors-headers) and instead:
    - allow origins listed in settings.CORS_ALLOWED_ORIGINS
    - handle preflight (OPTIONS) requests
    - expose our custom headers (X-ROLE, X-USER, X-API-KEY)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_origins = getattr(
            settings,
            "CORS_ALLOWED_ORIGINS",
            ["http://localhost:3000", "http://127.0.0.1:3000"],
        )

    def __call__(self, request):
        origin = request.headers.get("Origin")

        # Handle preflight requests early
        if request.method == "OPTIONS" and origin in self.allowed_origins:
            response = HttpResponse()
            self._add_cors_headers(response, origin)
            return response

        response = self.get_response(request)
        if origin in self.allowed_origins:
            self._add_cors_headers(response, origin)
        return response

    @staticmethod
    def _add_cors_headers(response, origin: str) -> None:
        response["Access-Control-Allow-Origin"] = origin
        response["Vary"] = "Origin"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization, X-ROLE, X-USER, X-API-KEY"
        )
        response["Access-Control-Allow-Credentials"] = "true"

