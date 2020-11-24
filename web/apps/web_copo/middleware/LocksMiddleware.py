from web.apps.web_copo.models import ViewLock
class LocksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_anonymous:
            return self.get_response(request)
        else:
            locks = ViewLock.objects.filter(user=request.user)
            url = request.build_absolute_uri()
            for l in locks:
                if l.url != url:
                    l.delete_self()
            response = self.get_response(request)
            return response