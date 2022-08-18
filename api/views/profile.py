from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny


class APICreateProfile(APIView):
    def post(self, request):
        x = {"text": "abc"}
        return Response(x)
