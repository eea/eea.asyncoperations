""" Events
"""
from zope.component.interfaces import IObjectEvent


class IAsyncOperationsEvent(IObjectEvent):
    """ Base Event Interface for all Async events
    """


class IAsyncOperationAdded(IAsyncOperationsEvent):
    """ Async job added
    """


class IAsyncMoveSuccess(IAsyncOperationsEvent):
    """ Async job for move succeeded
    """


class IAsyncMoveFail(IAsyncOperationsEvent):
    """ Async job for move failed
    """


class IAsyncRenameSuccess(IAsyncOperationsEvent):
    """ Async job for rename succeeded
    """


class IAsyncRenameFail(IAsyncOperationsEvent):
    """ Async job for rename failed
    """


class IAsyncOperationsSaveProgress(IAsyncOperationsEvent):
    """ Async job for save move progress
    """
