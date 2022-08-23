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
        # first check if there is a profile with this title already
        existing_profiles = Profile().get_collection_handle().find({"user_id": uid, "title": request.POST["title"]})
        if len(list(existing_profiles)) > 0:
            return Response(status=409, data={"status": "A Profile with that name already exists:" + request.POST["title"]})
        p_dict = {"title": request.POST["title"], "description": request.POST["description"], "type": request.POST["profile_type"],
                  "user_id": uid}
        p = Profile().save_record({}, **p_dict)
        out = {"_id": str(p["_id"]), "title": p["title"], "description": p["description"], "type": p["type"]}
        return Response(out)


class APIGetProfilesForUser(APIView):
    def post(self, request):
        uid = request.user.id
        existing_profiles = Profile().get_collection_handle().find({"user_id": uid})
        out = list()
        for el in existing_profiles:
            out.append({"title": el["title"], "_id": str(el["_id"])})
        return Response(out)
