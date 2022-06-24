from web.apps.web_copo.models import StatusMessage


def latest_message(request):
    sm = StatusMessage(message_owner=request.user, message="hello world")
    sm.save()
    status_msgs = request.user.statusmessage_set.latest()

    return {"latest_message": status_msgs.message, "created": status_msgs.created}
