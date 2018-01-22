from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "x-http-api-key"
    HTTP header.
    """
    def authenticate(self, request):
        try:
            white_list = settings.QUERY_WHITE_LIST
            valid_api_keys = settings.QUERY_API_KEYS
        except AttributeError:
            raise ImproperlyConfigured(
                'You have to provide QUERY_WHITE_LIST and QUERY_API_KEYS as '
                'tuples or lists in the project\'s settings.py.'
            )
        api_key = request.META.get('HTTP_X_HTTP_API_KEY')

        if not api_key:
            return None

        if api_key in valid_api_keys:
            return (AnonymousUser(), api_key)

        raise AuthenticationFailed('Invalid token.')
