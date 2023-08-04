from django.urls import path
from . import consumers

# as_asgi() is added to fix the TypeError: __call__() missing 1 required positional argument: 'send'

websocket_urlpatterns = [
    path('ws/submission_status/<str:profile_id>/', consumers.SubmissionConsumer),
    path('ws/sample_status/<str:profile_id>', consumers.SampleConsumer),
    path('ws/dtol_status', consumers.DtolConsumer),
    path('ws/s3_status/<str:uid>', consumers.s3Consumer),
    path('ws/assembly_status/<str:profile_id>', consumers.assemblyConsumer),
    path('ws/annotation_status/<str:profile_id>', consumers.annotationConsumer),
    path('ws/read_status/<str:uid>', consumers.readConsumer),
    path('ws/tagged_seq_status/<str:uid>', consumers.taggedSeqConsumer)
]