from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/submission_status/<str:profile_id>/', consumers.SubmissionConsumer),
    path('ws/sample_status/<str:profile_id>', consumers.SampleConsumer),
    path('ws/dtol_status', consumers.DtolConsumer),
    path('ws/s3_status/<str:uid>', consumers.s3Consumer)
]
