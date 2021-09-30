__author__ = 'felix.shaw@tgac.ac.uk - 27/05/2016'

from django.http import HttpResponse

from dal.copo_da import Submission
from . import figshareSubmission, dataverseSubmission, dspaceSubmission, ckanSubmission
from django.urls import reverse
import jsonpickle, json
from bson import ObjectId
from dal import cursor_to_list


def delegate_submission(request):
    """
    function delegates incoming submission request to handlers based on repository type
    :param request:
    :return:
    """
    sub_id = request.POST.get('submission_id', str())

    if not sub_id:
        sub_id = request.GET.get('submission_id', str())

    # submission record id not received
    if not sub_id:
        context = dict(status='error', message='Submission ID not found! Please try resubmitting with a valid ID.')
        out = jsonpickle.encode(context, unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    # get submission record and dependencies
    doc = Submission().get_collection_handle().aggregate(
        [
            {"$addFields": {
                "destination_repo_converted": {
                    "$convert": {
                        "input": "$destination_repo",
                        "to": "objectId",
                        "onError": 0
                    }
                },
            }
            },
            {
                "$lookup":
                    {
                        "from": "RepositoryCollection",
                        "localField": "destination_repo_converted",
                        "foreignField": "_id",
                        "as": "repository_docs"
                    }
            },
            {
                "$project": {
                    "repository_docs.type": 1,
                    "bundle": 1
                }
            },
            {
                "$match": {
                    "_id": ObjectId(str(sub_id)),
                }
            },
            {"$sort": {"date_modified": 1}}
        ])

    records = cursor_to_list(doc)

    # get submission record
    try:
        sub = records[0]
    except (IndexError, AttributeError) as error:
        context = dict(status='error', message='Submission record not found. Please try resubmitting.')
        out = jsonpickle.encode(context, unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    # get repository type
    try:
        repo = sub['repository_docs'][0]['type']
    except (IndexError, AttributeError) as error:
        # destination repository record not found
        context = dict(status='error', message='Repository information not found. Please contact an administrator.')
        out = jsonpickle.encode(context, unpicklable=False)
        return HttpResponse(out, content_type='application/json')

    #  Submit to Figshare
    if repo == 'figshare':

        # check figshare credentials
        if figshareSubmission.FigshareSubmit(sub_id).isValidCredentials(user_id=request.user.id):

            figshareSubmission.FigshareSubmit(sub_id).submit(
                sub_id=sub_id,
                dataFile_ids=sub['bundle'],

            )
            return HttpResponse(jsonpickle.dumps({'status': 1}))

        else:
            # forward to control view
            return HttpResponse(jsonpickle.dumps({'status': 1, 'url': reverse('copo:authenticate_figshare')}))

    # Submit to ENA Sequence reads
    elif repo in ['ena', 'ena-asm']:
        result = schedule_submission(submission_id=sub_id, submission_repo=repo)
        return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type='application/json')

    # Submit to Dataverse
    elif repo == 'dataverse':
        result = dataverseSubmission.DataverseSubmit(submission_id=sub_id).submit()
        return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type='application/json')

    # Submit to CKAN
    elif repo == 'ckan':
        result = ckanSubmission.CkanSubmit(submission_id=sub_id).submit()
        return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type='application/json')

    # Submit to dspace
    elif repo == 'dspace':
        result = dspaceSubmission.DspaceSubmit(submission_id=sub_id).submit()
        return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type='application/json')

    else:
        result = dict(status=False, message="Selected submission type not supported.")
        return HttpResponse(jsonpickle.encode(result, unpicklable=False), content_type='application/json')

def schedule_submission(submission_id=str(), submission_repo=str()):
    """
    function adds submission to a queue for processing
    :return:
    """

    from submission.helpers import generic_helper as ghlper
    import web.apps.web_copo.schemas.utils.data_utils as d_utils

    context = dict(status=True, message='')

    if not submission_id:
        context = dict(status=False, message='Submission identifier not found!')
        return context

    collection_handle = ghlper.get_submission_queue_handle()
    doc = collection_handle.find_one({"submission_id": submission_id})

    if not doc:  # submission not in queue, add to queue
        fields = dict(
            submission_id=submission_id,
            date_modified=d_utils.get_datetime(),
            repository=submission_repo,
            processing_status='pending'
        )

        collection_handle.insert(fields)
        context['message'] = 'Submission has been added to the processing queue. Status update will be provided.'
    else:
        context['message'] = 'Submission is already in the processing queue.'

    ghlper.update_submission_status(status='info', message=context['message'], submission_id=submission_id)
    ghlper.logging_info(context['message'], submission_id)

    return context
