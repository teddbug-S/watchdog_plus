# MIT License
#
# Copyright (c) 2023 Divine Decimate Darkey ( D.Cube )
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


from watchdog.observers import Observer


class WatchdogPlusObserver(Observer):
    """
    WatchdogObserverPlus directly subclasses watchdog.observers.Observer
    and overrides the `dispatch_events` method to dispatch each event with the
    name of the thread triggering that change.
    """

    def __init__(self):
        super().__init__()

    def dispatch_events(self, event_queue):
        event, watch = event_queue.get(block=True)

        with self._lock:
            # To allow unschedule/stop and safe removal of event handlers
            # within event handlers itself, check if the handler is still
            # registered after every dispatch.
            for handler in list(self._handlers.get(watch, [])):
                if handler in self._handlers.get(watch, []):
                    handler.dispatch(event, self.name)
        event_queue.task_done()


__all__ = ["WatchdogPlusObserver"]
