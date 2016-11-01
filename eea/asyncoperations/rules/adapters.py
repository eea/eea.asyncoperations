""" Content-rules string substitution
"""
from plone.stringinterp.adapters import BaseSubstitution


class FolderMoveFrom(BaseSubstitution):
    """ Move folder from substitution
    """
    category = u'asyncoperations'
    description = u'Move folder from'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'folder_move_from', '')


class FolderMoveTo(BaseSubstitution):
    """ Move folder to substitution
    """
    category = u'asyncoperations'
    description = u'Move folder to'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'folder_move_to', '')


class FolderMoveObjects(BaseSubstitution):
    """ Move folder objects substitution
    """
    category = u'asyncoperations'
    description = u'Move folder objects'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'folder_move_objects', '')


class FolderMoveEmail(BaseSubstitution):
    """ Move folder email substitution
    """
    category = u'asyncoperations'
    description = u'Move folder e-mail'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'async_operations_email', '')


class AsyncOperationsError(BaseSubstitution):
    """ error message substitution
    """
    category = u'asyncoperations'
    description = u'Error message'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'error', '')


class AsyncOperationsJobID(BaseSubstitution):
    """ job id substitution
    """
    category = u'asyncoperations'
    description = u'Job ID'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'job_id', '')


class AsyncOperationsQueueLength(BaseSubstitution):
    """ Async queue length
    """
    category = u'asyncoperations'
    description = u'Queue length for async operations'

    def safe_call(self):
        """ Safe call
        """
        length = self.context.restrictedTraverse('@@async_queue_length')
        if length:
            return length() - 1
        return 0


class AsyncOperationsOperationType(BaseSubstitution):
    """ job id substitution
    """
    category = u'asyncoperations'
    description = u'Async operation type'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'async_operation_type', 'move')
