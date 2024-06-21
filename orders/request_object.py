# Custom middleware to get the vendor in the models.py
from . import models

def RequestObjectMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        models.request_object = request

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware