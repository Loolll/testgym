from rest_framework.authentication import SessionAuthentication, BasicAuthentication, BaseAuthentication
from django.contrib.auth import authenticate
from django.contrib.auth import logout, login


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def api_user_authentication(request):
    email = request.META.get('HTTP_EMAIL')
    password = request.META.get('HTTP_PASSWORD')
    if email is not None and password is not None:
        user = authenticate(request, email=email, password=password)
        if user is not None:
            return user

    return None
