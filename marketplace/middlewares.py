class AjaxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def is_ajax(self):
            return request.headers.get('x-requested-with') == 'XMLHttpRequest'
        
        request.is_ajax = is_ajax.__get__(request)
        response = self.get_response(request)
        return response