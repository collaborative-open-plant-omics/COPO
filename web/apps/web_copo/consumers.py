from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
import asyncio
from django_tools.middlewares import ThreadLocal


class SubmissionConsumer(WebsocketConsumer):
    def connect(self):
        self.profile_id = self.scope['url_route']['kwargs']['profile_id']
        self.group_name = 'submission_status_%s' % self.profile_id

        # join group
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # leave group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    # receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # send message to group`
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': text_data_json['type'],
                'message': text_data_json['message']
            }
        )

    # receive message from group
    def submission_status(self, event):
        # send message to WebSocket
        self.send(text_data=json.dumps(event))

    # receive message from group
    def file_transfer_status(self, event):
        # send message to WebSocket
        self.send(text_data=json.dumps(event))


class SampleConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.profile_id = self.scope['url_route']['kwargs']['profile_id']
        self.group_name = 'sample_status_%s' % self.profile_id

        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'msg',
                'message': message
            }
        )

    async def msg(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event["message"],
            'action': event["action"],
            'html_id': event["html_id"]
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


class DtolConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.group_name = 'dtol_status'

        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'msg',
                'message': message
            }
        )

    async def msg(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event["message"],
            'action': event["action"],
            'html_id': event["html_id"],
            'data': event["data"]
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


class s3Consumer(AsyncWebsocketConsumer):
    """
    Class to communicate s3 information. To target this, use s3_ as suffix for group name
    notify_frontend(data={"profile_id": profile_id}, msg="", action="info",
                                    html_id="sample_info", group_name=s3_profile_id)

    open a javascript web socket connecting to path('ws/s3_status/<str:uid>', consumers.s3Consumer)
    """

    async def connect(self):
        gn = "s3_" + self.scope['url_route']['kwargs']['uid']
        self.group_name = gn
        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'msg',
                'message': message
            }
        )

    async def msg(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event["message"],
            'action': event["action"],
            'html_id': event["html_id"],
            'data': event["data"]
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

class assemblyConsumer(AsyncWebsocketConsumer):
    """
    Class to communicate assembly information. To target this, use assembly_ as suffix for group name
    notify_frontend(data={"profile_id": profile_id}, msg="", action="info",
                                    html_id="sample_info", group_name=assembly_profile_id)

    open a javascript web socket connecting to path('ws/assembly_status/<str:uid>', consumers.assemblyConsumer)
    """

    async def connect(self):
        gn = "assembly_status_" + self.scope['url_route']['kwargs']['profile_id']
        self.group_name = gn
        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'msg',
                'message': message
            }
        )

class annotationConsumer(AsyncWebsocketConsumer):
    """
    Class to communicate annotation information. To target this, use annotation_ as suffix for group name
    notify_frontend(data={"profile_id": profile_id}, msg="", action="info",
                                    html_id="sample_info", group_name=annotation_profile_id)

    open a javascript web socket connecting to path('ws/annotation_status/<str:uid>', consumers.annotationConsumer)
    """

    async def connect(self):
        gn = "annotation_status_" + self.scope['url_route']['kwargs']['profile_id']
        self.group_name = gn
        # join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # send message to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'msg',
                'message': message
            }
        )


    async def msg(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event["message"],
            'action': event["action"],
            'html_id': event["html_id"],
            'data': event["data"]
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
