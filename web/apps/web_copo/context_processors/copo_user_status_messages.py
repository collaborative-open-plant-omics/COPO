from web.apps.web_copo.models import StatusMessage
from datetime import datetime


def latest_message(request):
    '''
    sm = StatusMessage(message_owner=request.user, message="")
    sm.save()
    '''
    try:
        if request.user.userdetails.active_task:
            status_msgs = request.user.statusmessage_set.latest()
            return {"latest_message": status_msgs.message, "created": status_msgs.created}
        else:
            return {"latest_message": "No Active Tasks", "created": datetime.utcnow()}
    except:
        return {}
