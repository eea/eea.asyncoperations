""" Async events
"""
from zope.interface import implementer
from eea.asyncoperations.events import AsyncOperationsEvent
from eea.asyncoperations.events.interfaces import IAsyncMoveFail
from eea.asyncoperations.events.interfaces import IAsyncMoveSuccess
from eea.asyncoperations.events.interfaces import IAsyncOperationAdded
from eea.asyncoperations.events.interfaces import IAsyncRenameSuccess
from eea.asyncoperations.events.interfaces import IAsyncRenameFail
from eea.asyncoperations.events.interfaces import IAsyncOperationsSaveProgress


@implementer(IAsyncOperationAdded)
class AsyncOperationAdded(AsyncOperationsEvent):
    """ Event triggered when an async job was added
    """


@implementer(IAsyncMoveFail)
class AsyncMoveFail(AsyncOperationsEvent):
    """ Event triggered when an async move job failed
    """


@implementer(IAsyncMoveSuccess)
class AsyncMoveSuccess(AsyncOperationsEvent):
    """ Event triggered when an async move job succeeded
    """


@implementer(IAsyncRenameSuccess)
class AsyncRenameSuccess(AsyncOperationsEvent):
    """ Event triggered when an async move job succeeded
    """


@implementer(IAsyncRenameFail)
class AsyncRenameFail(AsyncOperationsEvent):
    """ Event triggered when an async rename job failed
    """


@implementer(IAsyncOperationsSaveProgress)
class AsyncOperationsSaveProgress(AsyncOperationsEvent):
    """ Event triggered when an async job saved its progress
    """
