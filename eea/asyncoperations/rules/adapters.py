""" Content-rules string substitution
"""
from plone.stringinterp.adapters import BaseSubstitution


class ObjectMoveFrom(BaseSubstitution):
    """ Move object from substitution
    """
    category = u'asyncoperations'
    description = u'Move object from'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'object_move_from', '')


class ObjectMoveTo(BaseSubstitution):
    """ Move object to substitution
    """
    category = u'asyncoperations'
    description = u'Move object to'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'object_move_to', '')


class ObjectsToMove(BaseSubstitution):
    """ Move objects substitution
    """
    category = u'asyncoperations'
    description = u'Move objects'

    def safe_call(self):
        """ Safe call
        """
        return getattr(self.wrapper, 'objects_to_move', '')


class ObjectMoveEmail(BaseSubstitution):
    """ Move object email substitution
    """
    category = u'asyncoperations'
    description = u'Move object e-mail'

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
