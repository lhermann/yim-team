from django.conf import settings
from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to access.
    """
    message = 'No owner.'

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id

class WhiteListAndAPIKey(permissions.BasePermission):
    """
    Permission check for whitelisted IPs and API keys.
    """
    message = 'Invalid or missing IP address or API Key.'

    def has_permission(self, request, view):
        ip = request.META.get('REMOTE_ADDR')
        api_key = request.META.get('x-http-api-key')
        white_list = settings.QUERY_WHITE_LIST
        valid_api_keys = settings.QUERY_API_KEYS
        if ip in white_list and api_key in valid_api_keys:
            return True
        if request.user.is_superuser:
            return True
        return False


def generate_key():
    """
    Generate an API key.
    """
    # Source: https://github.com/manosim/django-rest-framework-api-key
    import binascii
    import os
    return binascii.hexlify(os.urandom(20)).decode()
