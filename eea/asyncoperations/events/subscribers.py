""" Subscribers
"""
import os
import logging
from plone.app.async.subscribers import set_quota
from zope.annotation import IAnnotations
from Products.CMFCore.utils import getToolByName
logger = logging.getLogger('eea.asyncoperations')


def getMaximumThreads(queue):
    """ Get the maximum threads per queue
    """
    size = 0
    for da in queue.dispatchers.values():
        if not da.activated:
            continue
        for _agent in da.values():
            size += 3
    return size or 1


def configureQueue(event):
    """ Configure zc.async queue for bulk async jobs
    """
    queue = event.object

    try:
        size = int(os.environ.get('EEASYNCOPERATIONS_ASYNC_THREADS',
                                  getMaximumThreads(queue)))
    except Exception, err:
        logger.exception(err)
        size = 1

    set_quota(queue, 'asyncoperations', size=size)
    logger.info(
        "quota 'asyncoperations' with size %r configured in queue %r.",
        size, queue.name)


def saveJobProgress(event):
    """ Save job progress
    """
    portal = getToolByName(event.object, 'portal_url').getPortalObject()
    portal_anno = IAnnotations(portal)
    annotation = portal_anno.get('async_operations_jobs')
    annotation_job = annotation.setdefault(event.job_id, {})

    if event.operation == 'initialize':
        annotation_job['sub_progress'] = {}
        operation_type = getattr(event, 'operation_type', 'Moved')
        annotation_job['title'] = "%s below objects within: %s" % (
            operation_type, event.object.absolute_url()
        )

        for oid, title in event.oblist_id:
            annotation_job['sub_progress'][oid] = {}
            annotation_job['sub_progress'][oid]['progress'] = 0
            annotation_job['sub_progress'][oid]['title'] = title

    if event.operation == 'sub_progress':
        obj_id = event.obj_id
        annotation_job.setdefault('sub_progress', {})
        annotation_job['sub_progress'].setdefault(obj_id, {})
        annotation_job['sub_progress'][obj_id]['progress'] = event.progress

    if event.operation == 'progress':
        annotation_job['progress'] = event.progress
