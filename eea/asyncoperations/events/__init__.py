""" Events
"""
from zope.interface import implementer
from eea.asyncoperations.events.interfaces import IAsyncOperationsEvent


@implementer(IAsyncOperationsEvent)
class AsyncOperationsEvent(object):
    """ Abstract event for all async events
    """
    def __init__(self, context, **kwargs):
        self.object = context
        for key, value in kwargs.items():
            setattr(self, key, value)
