""" Browser views for Async Operations
"""
import json
import logging
from BTrees.OOBTree import OOBTree
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
from plone.app.async.interfaces import IAsyncService
from plone.app.async.browser.queue import JobsJSON
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.stringinterp.interfaces import IContextWrapper
from plone import api
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import queryUtility
from zope.event import notify
from zc.async.utils import custom_repr
from ZODB.utils import u64
from ZODB.POSException import ConflictError
from OFS.CopySupport import cookie_path, _cb_decode, CopyError
from OFS.CopySupport import eInvalid, eNotFound, eNoItemsSpecified
from OFS.Moniker import loadMoniker
from eea.asyncoperations.config import EEAMessageFactory as _
from eea.asyncoperations.async import async_move, JOB_PROGRESS_DETAILS
from eea.asyncoperations.async import async_rename
from eea.asyncoperations.events.async import AsyncOperationAdded
from eea.asyncoperations.events.async import AsyncMoveSuccess, AsyncMoveFail
from eea.asyncoperations.events.async import AsyncRenameSuccess, AsyncRenameFail

logger = logging.getLogger('eea.asyncoperations')
ASYNCOPERATIONS_QUEUE = 'asyncoperations'


class AsyncConfirmation(BrowserView):
    """ action confirmation
    """

    def objects_to_async(self, request_key='__cp'):
        """ get info of files to perform async operation
        """

        newid = self.request.get(request_key)

        if not newid:
            raise CopyError(eNoItemsSpecified)

        try:
            _op, mdatas = _cb_decode(newid)
        except:
            raise CopyError(eInvalid)

        oblist = []
        app = self.context.getPhysicalRoot()

        for mdata in mdatas:
            m = loadMoniker(mdata)
            try:
                ob = m.bind(app)
            except ConflictError:
                raise
            except:
                raise CopyError(eNotFound)

            oblist.append(ob)

        return oblist


class MoveAsync(BrowserView):
    """ Ping action executor
    """
    def _redirect(self, msg, msg_type='info', redirect_to='/async_operation'):
        """ Set status message to msg and redirect to context absolute_url
        """
        if self.request:
            url = self.context.absolute_url() + redirect_to
            IStatusMessage(self.request).addStatusMessage(msg, type=msg_type)
            self.request.response.redirect(url)
        return msg

    def _cleanup(self):
        """ Cleanup __cp from self.request
        """
        if self.request is not None:
            self.request.response.setCookie('__cp', 'deleted',
                path='%s' % cookie_path(self.request),
                expires='Wed, 31-Dec-97 23:59:59 GMT'
            )
            self.request['__cp'] = None

    def original_action(self, action='paste'):
        """ Plone synchronous action
        """
        try:
            obj_action = 'object_' + action
            object_action = self.context.restrictedTraverse(obj_action)
            object_action()
        except Exception, err:
            logger.exception(err)
            msg = _(u"Can't %s item(s) here: %s", action, err)
        else:
            msg = _(u"Item(s) %s.", action)

        self._cleanup()
        redirect_to = '/async_operation' if action == 'paste' else ''
        return self._redirect(msg, redirect_to=redirect_to)

    def post(self, **kwargs):
        """ POST
        """
        newid = self.request.get('__cp')
        if 'form.button.Cancel' in kwargs:
            return self._redirect(_(u"Paste cancelled"))
        elif 'form.button.paste' in kwargs:
            return self.original_action()
        elif 'form.button.async' not in kwargs:
            return self.index()

        worker = getUtility(IAsyncService)
        queue = worker.getQueues()['']

        try:
            job = worker.queueJobInQueue(
                queue, (ASYNCOPERATIONS_QUEUE,),
                async_move,
                self.context, newid=newid,
                success_event=AsyncMoveSuccess,
                fail_event=AsyncMoveFail,
                email=api.user.get_current().getProperty('email')
            )
            job_id = u64(job._p_oid)

            anno = IAnnotations(self.context)
            anno['async_operations_job'] = job_id
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal_anno = IAnnotations(portal)
            if not portal_anno.get('async_operations_jobs'):
                portal_anno['async_operations_jobs'] = OOBTree()

            message_type = 'info'
            message = _(u"Item added to the queue. "
                        u"We will notify you when the job is completed")

            self._cleanup()
        except Exception, err:
            logger.exception(err)
            message_type = 'error'
            message = u"Failed to add items to the sync queue"

        return self._redirect(message, message_type)

    def __call__(self, *args, **kwargs):
        kwargs.update(getattr(self.request, 'form', {}))
        if self.request.method.lower() == 'post':
            return self.post(**kwargs)
        return self.index()


class RenameAsync(MoveAsync):
    """ RenameAsync
    """
    def post(self, **kwargs):
        """ POST
        """
        newids = self.request.get('new_ids')
        newtitles = self.request.get('new_titles', '')
        paths = self.request.get('paths', '')
        if 'form.button.Cancel' in kwargs:
            return self._redirect(_(u"Rename cancelled"), redirect_to='')
        elif 'form.button.rename' in kwargs:
            return self.original_action(action='rename')
        elif 'form.button.async_rename' in kwargs:
            return self.index()

        worker = getUtility(IAsyncService)
        queue = worker.getQueues()['']
        email = api.user.get_current().getProperty('email')

        try:
            job = worker.queueJobInQueue(
                queue, (ASYNCOPERATIONS_QUEUE,),
                async_rename,
                self.context,
                new_ids=newids,
                new_titles=newtitles,
                paths=paths,
                success_event=AsyncRenameSuccess,
                fail_event=AsyncRenameFail,
                email=email
            )
            job_id = u64(job._p_oid)

            context = self.context
            wrapper = IContextWrapper(context)(
                object_move_from=context.absolute_url(1),
                object_move_to=', '.join(newids),
                objects_to_move=', '.join(paths),
                async_operations_email=email,
                async_operation_type='rename',
                email=email
            )
            notify(AsyncOperationAdded(wrapper))

            anno = IAnnotations(self.context)
            anno['async_operations_job'] = job_id
            portal = getToolByName(self, 'portal_url').getPortalObject()
            portal_anno = IAnnotations(portal)
            if not portal_anno.get('async_operations_jobs'):
                portal_anno['async_operations_jobs'] = OOBTree()

            message_type = 'info'
            message = _(u"Item added to the queue. "
                        u"We will notify you by email at '%s' when the job is "
                        u"completed" % email)
        except Exception, err:
            logger.exception(err)
            message_type = 'error'
            message = u"Failed to add items to the sync queue"

        return self._redirect(message, message_type)


class AsyncOperationsQueueJSON(JobsJSON):
    """ queue json
    """

    def _filter_jobs(self):
        """ Filter jobs
        """
        for job_status, job in self._find_jobs():
            if len(job.args) == 0:
                continue
            job_context = job.args[0]
            if (isinstance(job_context, tuple) and
                job_context[:len(self.portal_path)] == self.portal_path and
                ASYNCOPERATIONS_QUEUE in job.quota_names):
                yield job_status, job

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        jobs = {
            'queued': [],
            'active': [],
            'completed': [],
            'dead': [],
        }

        for job_status, job in self._filter_jobs():
            jobs[job_status].append({
                'id': u64(job._p_oid),
                'callable': self.format_title(job),
                'args': self.format_args(job),
                'status': self.format_status(job),
                'progress': self.format_progress(job),
                'sub_progress': self.format_subprogress(job),
                'failure': self.format_failure(job),
                'operation': job.args[-1].__name__.split('_')[1],
                'user': job.args[-2],
                'started': self.format_datetime(job.active_start) if \
                        job.active_start else '',
                'objects': '\n '.join(job.kwargs.get('paths', []))
            })

        return json.dumps(jobs)

    def get_job_annotation(self, job):
        """ Get job annotation
        """
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        portal_anno = IAnnotations(portal)
        async_job_status = portal_anno.get('async_operations_jobs')
        if async_job_status:
            job_id = u64(job._p_oid)
            annotation_job = async_job_status.get(job_id)
            return annotation_job
        return None

    def format_title(self, job):
        """ Title format
        """
        annotation = self.get_job_annotation(job)
        custom_title = custom_repr(job.callable)
        if not annotation:
            return custom_title

        title = annotation.get('title', custom_title)
        return title

    def format_progress(self, job):
        """ Format progress
        """
        annotation = self.get_job_annotation(job)
        if not annotation:
            return ''

        progress = annotation.get('progress', 0.0) * 100
        if not progress:
            return ''

        return """ <div class='job-item'><div class="progress-bar"
                    style="width:%d%%;">
                    &nbsp;</div> %d%% %s</div>""" % (progress, progress,
                                                     self.format_status(job))

    def format_subprogress(self, job):
        """ Format sub-progress
        """
        sub_progresses = []

        annotation = self.get_job_annotation(job)
        if not annotation:
            return ''

        progresses = annotation.get('sub_progress', [])
        if not progresses:
            return ''

        for key, progress in progresses.items():
            title = progress.get('title', 'id: ' + key)
            value = progress['progress'] * 100
            detail = JOB_PROGRESS_DETAILS.get(value, '')
            sub_progresses.append(
                """ <div class='job-item' id="%s">
                    <div><strong>%s</strong></div>
                    <div class="progress-bar" style="width:%d%%;">&nbsp;</div>
                    %d%% %s</div> """ % (key, title, value, value, detail))

        return ''.join(sub_progresses)


class AsyncOperationsStatus(BrowserView):
    """ queue status
    """

    def js(self, timeout=10000):
        """Returns the javascript code for async call
        """
        return """
jQuery(function($) {
  var update = function() {
    var escape = function(s) {
        return s.replace('<', '&lt;').replace('>', '&gt;');
    }

    $.fn.render = function(data, queue) {
      var rows = ['<caption style="width:100%%;">'];
      rows.push('<div class="portalMessage informationMessage">');
      rows.push('The list is refreshed every %(seconds)s seconds.');
      rows.push('</div></caption>');
      rows.push('<tr><th>Job</th><th>Started</th><th>Status</th>' +
                '<th>By user</th><th>Operation type</th>');
      if (queue && queue === 'active') {
        rows.push('<th>Objects</th></tr>');
      }
      else {
        rows.push('</tr>');
      }
      $(data).each(function(i, job) {
        row = ['<tr><td><div class="job-item"><strong>' + escape(job.callable) +
          '</strong></div>'];
        if (job.sub_progress)
          row.push(job.sub_progress);
        row.push('</td>');
        row.push('<td>');
        row.push(job.started);
        row.push('</td>');
        row.push('<td>');
        if (job.progress)
          row.push(job.progress);
        else
          row.push(job.status);
        if (job.failure)
          row.push('<div>' + job.failure + '</div>')
        row.push('</td>');
        if (job.user) {
          row.push('<td>');
          row.push(job.user);
          row.push('</td>');
        }
        if (job.operation) {
          row.push('<td>');
          row.push(job.operation);
          row.push('</td>');
        }
        if (job.objects && (queue && queue ==='active')) {
          row.push('<td class="pre-wrap">');
          row.push(job.objects);
          row.push('</td>');
        }
        rows.push(row.join('') + '</tr>');
      });
      $('table', this).html(rows.join(''));
      var form = this.closest('form');
      var legend = $('legend', this);
      $('.formTab span', form).eq($('legend', form).
        index(legend)).html(legend.html().replace('0', data.length));
    };

    $.getJSON('async_operations_queue.json', {
            'ajax_load': new Date().getTime()
        }, function(data) {
      $('#queued-jobs').render(data.queued);
      $('#active-jobs').render(data.active, queue='active');
      $('#dead-jobs').render(data.dead);
      $('#completed-jobs').render(data.completed);
    });

    setTimeout(update, %(timeout)s);
  };
  update();
  });
""" % {'seconds': timeout/1000, 'timeout': timeout}


class ContentRuleCleanup(BrowserView):
    """ ContentRuleCleanup
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """ Change conditions to use absolute_url instead of request
        """
        log = logging
        log.info("Starting check of content rules tales expression")
        storage = queryUtility(IRuleStorage)
        if not storage:
            return
        rules = storage.values()
        result = ["Removing request from content rules tales expressions:"]
        for rule in rules:
            conditions = rule.conditions
            for condition in conditions:
                if len(condition) > 1:
                    condition = condition[0]
                tales = getattr(condition, 'tales_expression', None)
                if tales:
                    log.info("%s rule has '%s' tales_expression", rule.id,
                             tales)
                    if 'REQUEST.URL' in tales:
                        condition.tales_expression = tales.replace(
                            'REQUEST.URL', 'absolute_url()')
                        wmsg = "'%s' tales_expression changed '%s' --> '%s'" % (
                                    rule.id, tales, condition.tales_expression)
                        log.warn(wmsg)
                        result.append(wmsg)
        return "\n".join(result)


class AsyncQueueLength(BrowserView):
    """ Current length of queued async operations
    """
    def __call__(self):
        """ call
        """
        service = getUtility(IAsyncService)
        return len(service.getQueues()[''])
