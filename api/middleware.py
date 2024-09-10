from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout

import time
from datetime import datetime, timedelta

from rest_framework.authtoken.models import Token


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not request.user.is_authenticated:
            header = request.headers.get('Authorization')
            if header:
                try:
                    token_type, token = header.split(' ')
                    if token_type.lower() == 'token':
                        Token.objects.filter(key=token).delete()
                except ValueError:
                    print("Invalid Authorization header format")

        if hasattr(request, 'user') and request.user.is_authenticated:
            current_time = datetime.now()
            last_activity = request.session.get('last_activity')
            print((request.user.is_authenticated))
            if last_activity:
                last_activity = datetime.fromtimestamp(last_activity)
                print((current_time))
                print((last_activity))
                print((current_time - last_activity).total_seconds())
                if (current_time - last_activity) > timedelta(seconds=settings.SESSION_IDLE_TIMEOUT):
                    header = request.headers.get('Authorization')
                    if header:
                        try:
                            token_type, token = header.split(' ')
                            if token_type.lower() == 'token':
                                Token.objects.filter(key=token).delete()
                        except ValueError:
                            print("Invalid Authorization header format")
                    logout(request)
            request.session['last_activity'] = time.time()

        response = self.get_response(request)
        return response
