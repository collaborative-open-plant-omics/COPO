# Created by fshaw at 11/06/2018
from dal.copo_da import Profile
from django.core.exceptions import PermissionDenied
from django_tools.middlewares.ThreadLocal import get_current_request


def user_is_staff(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        else:
            return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_allowed_access(user, *args, **kwargs):
    # check if user is logged in
    if user:
        # check if user owns profile
        r = get_current_request()

        # if there is no session profile id, we need extract it from the url
        tmp = r.path.split("/")
        if tmp[-1] == "view":
            # we are dealing with a standard COPO url type....this is unfortunately a crap way of doing this
            p_id = tmp[-2]
        else:
            return False
        p = Profile().get_record(p_id)
        if p["user_id"] == user.id:
            return True
        # now check if profile is shared with user
        p_shared = Profile().get_shared_for_user()
        for p in p_shared:
            if str(p["_id"]) == p_id:
                return True
        return False
    return False
