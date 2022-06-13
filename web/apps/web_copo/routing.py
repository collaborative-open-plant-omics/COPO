from django.urls import path
from . import consumers

# as_asgi() is added to prevent the TypeError: __call__() missing 1 required positional argument: 'send'

websocket_urlpatterns = [
    path('ws/submission_status/<str:profile_id>/', consumers.SubmissionConsumer.as_asgi()),
    path('ws/sample_status/<str:profile_id>', consumers.SampleConsumer.as_asgi()),
    path('ws/dtol_status', consumers.DtolConsumer.as_asgi())
]
