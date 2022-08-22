from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
from bson import json_util
from dal.copo_da import Profile


class APICreateProfile(APIView):
    def post(self, request):
        uid = request.user.id
        p_dict = {"title": request.POST["title"], "description": request.POST["description"], "profile_type": request.POST["profile_type"],
                  "user_id": uid}
        p = Profile().save_record({}, **p_dict)
        return HttpResponse(json_util.dumps(p))
