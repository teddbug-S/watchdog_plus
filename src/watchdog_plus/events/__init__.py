# MIT License
#
# Copyright (c) 2022 Divine Darkey
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from os import path as os_path
import logging

from watchdog.events import (
    EVENT_TYPE_CLOSED,
    EVENT_TYPE_CREATED,
    EVENT_TYPE_DELETED,
    EVENT_TYPE_MODIFIED,
    EVENT_TYPE_MOVED,
    FileSystemEventHandler,
)


class WatchdogPlusBaseEventHandler(FileSystemEventHandler):
    """
    A base event handler for any file system event.
    It is recommended to subclass this class for any
    custom event handler definitions.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def dispatch(self, event, name):
        """
        Dispatches events to the appropriate methods.
        Args:
            name:
                Name of the path monitor triggering the event.
            event:
                The event object representing the file system event.
        Types:
            event:
                :class:`FileSystemEvent`
        """

        self.on_any_event(event, name)
        {
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CLOSED: self.on_closed,
        }[event.event_type](event, name)

    def on_any_event(self, event, name):
        return super().on_any_event(event)

    def on_created(self, event, name):
        return super().on_created(event)

    def on_modified(self, event, name):
        super().on_modified(event)

    def on_moved(self, event, name):
        super().on_moved(event)

    def on_closed(self, event, name):
        super().on_closed(event)

    def on_deleted(self, event, name):
        super().on_deleted(event)


class WatchdogPlusLogEventHandler(WatchdogPlusBaseEventHandler):
    """
    Logs any events to the console or to a file is any is specified.
    """

    def __init__(self, filter_modified: bool, log_file=None):
        super().__init__()

        self.filter_dir_modified = filter_modified
        self.log_file = log_file

        # configure the logger
        logging.basicConfig(
            format="%(message)s",
            filename=self.log_file,
            level=logging.INFO
        )

    def on_any_event(self, event, name):
        # filter unnecessary logging of directory modifications
        if self.filter_dir_modified and (os_path.isdir(event.src_path) and event.event_type == "modified"):
            return
        logging.info(f"<WatchDog: {name}> watched {event.src_path!r} got {event.event_type}")


__all__ = [
    'WatchdogPlusBaseEventHandler',
    'WatchdogPlusLogEventHandler'
]