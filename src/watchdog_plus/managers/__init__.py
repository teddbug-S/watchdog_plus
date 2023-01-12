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


import os
import typing
from concurrent import futures
from functools import partial
from enum import Enum
from signal import SIGKILL

from ..errors import AlreadyExists, DoesNotExist, ServiceNotFound
from ..events import WatchdogPlusLogEventHandler
from ..observers import WatchdogPlusObserver
from ..services import WatchDogPlusService


# Methods for starting an observer
class StartMethods(Enum):
    THREAD = 1
    MULTIPROCESS = 2


# A collection to keep observers
# and maintain uniqueness in their names
class ItemCollection(list):
    """An extension of builtins list structure to enforce uniqueness of items"""

    def append(self, value):
        # check for already existing name
        for item in self.__iter__():
            if item.name == value.name:
                raise AlreadyExists(
                    f"item with name {item.name!r} already exists")
        # else append to collections
        super().append(value)

    def get_item(self, name):
        """
        Returns an observer with name `name`
        :param name: name of observer to return
        :return: returns observer
        """
        for item in self.__iter__():
            if item.name == name:
                return item
        else:
            raise DoesNotExist(f"item with name {name} does not exist.")


class BaseObserverManager:
    """
    A class to manage, create, start and schedule observers.

    Initialization args:
        observer: An observer class which inherits from `watchdog.observers.Observer`

        handler:  An event handler which defines necessary methods for handling
                  dispatched events. Should inherit from `WatchdogPlusBaseEventHandler`
    """

    def __init__(self, observer=None, handler=None) -> None:
        self.ObserverClass = observer or WatchdogPlusObserver
        self.HandlerClass = handler or WatchdogPlusLogEventHandler

        # collection for observers
        self.observers = ItemCollection()

    @staticmethod
    def __start_observer(observer, duration: int = 0) -> None:
        """
        Starts an observer scheduled to monitor a path which
        lives for `duration` number of seconds.
        Args:
            observer: observer to start.
            duration: number of seconds to keep observer alive
                      defaults to zero which means forever.
        Note: observer maybe stopped by a keyboard interrupt.
        """
        observer.start()
        # keep observer ALIVE
        try:
            if duration:
                observer.join(duration)
            else:
                while True:
                    observer.join(1)
        except KeyboardInterrupt:
            # stop observer
            observer.stop()
            observer.join()

    def __start_observers(
            self, observers,
            duration: int, start_method: StartMethods = StartMethods.THREAD) -> None:

        """
        Starts a list of observers all at once using
        method specified in the `start_method` parameter.

        Args:
            observers: a list of observers to start
            start_method: the concurrent method to use in launching the observers
                defaults to threads which is equivalent to `StartMethods.THREAD`
        """
        max_workers = len(observers)  # get max number of workers
        # get names of workers
        names = tuple(observer.name for observer in observers)
        # using threads
        if start_method == StartMethods.THREAD:
            # initiate a thread pool executor max_workers equal to number of observers
            with futures.ThreadPoolExecutor(max_workers=max_workers) as thread_pool:
                # set name for each worker thread
                for worker, name in zip(thread_pool._threads, names):
                    worker.name = name
                # assign work
                thread_pool.map(partial(self.__start_observer, duration=duration), observers)
        # using processes
        elif start_method == StartMethods.MULTIPROCESS:
            # initiate a process pool executor max_workers equal to number of observers
            with futures.ProcessPoolExecutor(max_workers=max_workers) as process_pool:
                # set name for each worker process
                for process, name in zip(process_pool._processes, names):
                    process.name = name
                # assign work to each
                process_pool.map(partial(self.__start_observer, duration=duration), observers)

    # Public interfaces
    def observer_config(self, *args, **kwargs):
        """
        Apply extra configurations to the observer class before
        creating observers.

        This is useful when using with a custom observer class
        which requires some extra arguments.

        Arguments password to this method are in-turn passed to the observer
        class before use.
        """
        self.ObserverClass = partial(self.ObserverClass, *args, **kwargs)

    def handler_config(self, *args, **kwargs):
        """
        Apply extra configurations to the handler class before
        an observer is scheduled with the class.

        This is useful when using with a custom handler class
        which requires some extra arguments.

        Arguments password to this method are in-turn passed to the handler
        class before use.
        """
        self.HandlerClass = partial(self.HandlerClass, *args, **kwargs)

    def create_observer(self, path: str, name: str, recursive: bool = False) -> WatchdogPlusObserver:
        """
        Creates and returns and observer.
        Args:
            `path`: filesystem path for observer to monitor
            `name`: name of the observer
            `recursive`: whether observer should monitor child directories too.
        NOTE: all created observers are kept in `self.observers`.
        """
        # initialize an observer and schedule a handler.
        observer = self.ObserverClass()
        observer.schedule(self.HandlerClass(), path, recursive)

        observer.name = name
        self.observers.append(observer)

        return observer

    def create_observers(self, items: typing.Iterable, recursive: bool = False) -> typing.List[WatchdogPlusObserver]:
        """
        Create a number of observers from list of items
        containing pairs of path and name.
        """
        observers = [
            self.create_observer(pair[0], pair[1], recursive=recursive)  # for each pair create an observer
            for pair in items
        ]
        return observers

    def get_observer(self, name: str) -> WatchdogPlusObserver:
        """
        Retrieve an observer from `self.observers` with `name`
        """
        return self.observers.get_item(name)

    def start_observer(self, /, name: str = None, observer: WatchdogPlusObserver = None, duration: int = 0) -> None:
        """
        Starts an observer either by it's name or the object itself.
        Args:
            `name`: Optional, name of observer to start
            `observer`: Optional, observer object to start
            `duration`: Number of seconds you want observer to live.
        You must specify one and only one of these options.
        """
        observer = observer or self.get_observer(name)
        self.__start_observer(observer, duration)

    def start_observers(self, /, names: typing.Iterable[str] = None, observers=typing.Iterable[WatchdogPlusObserver],
                        duration: int = 0, start_method: StartMethods = StartMethods.THREAD) -> None:
        """
        Start a number of observers either by their names or objects itself.
        Args:
            `names`: Optional, a sequence of names of observers to start.
            `observers`: Optional, a sequence of observer objects to start.
            `duration`: number of seconds you want observers to live.
                        note that this is the same for all observers.
            `start_method`: start method to use in starting observers,
                            defaults to threads `StartMethods.THREAD`

        You must specify one and only one of these options.
        """
        # get observers
        observers = observers or tuple(self.get_observer(name) for name in names)
        self.__start_observers(observers=observers, duration=duration, start_method=start_method)


class ServiceManager:

    def __init__(self) -> None:
        self.Service_ = WatchDogPlusService
        self.services = ItemCollection()

    def create_service(self, path: typing.AnyStr, name: typing.AnyStr, output_file: typing.AnyStr,
                       service_dir: typing.AnyStr = None, handler: typing.Type = None):
        service = self.Service_(path=path, name=name, service_dir=service_dir)
        # handler import line
        handler_import = f"from {__name__} import {handler}\n" if handler else ""
        block = f"""
# generated by watchdog-service

# Imports if any
{handler_import}
from watchdog_plus.managers import ObserverManager

# path to monitor
path = {service.path!r}

# create an observer manager with a custom handler if any
manager = ObserverManager(handler={handler}) 
manager.create_observer(path, name={name!r}, log_file={output_file})

# launch observer
manager.start_observer({name})
                    """
        # write code block service file
        with open(service.service_file, "w") as file_:
            file_.write(block)

        # add observer to list of observers
        self.services.append(service)

    def clean_files(self, name: typing.AnyStr) -> None:
        """
        Deletes all files and directories created by a particular service
        """
        # get service
        service = self.services.get_item(name)
        service: WatchDogPlusService
        try:
            os.remove(service.service_file)
            os.remove(service.output_file)
        except FileNotFoundError:
            ...

    def start_service(self, name: typing.AnyStr) -> None:
        """launch a service"""
        service = self.services.get_item(name)
        # execute launch command
        os.system(service.launch_command)
        service.is_active = True

    def send_signal(self, name: typing.AnyStr, signal) -> None:
        """Send a signal to service"""
        service = self.services.get_item(name)
        if not service.is_active:
            raise ServiceNotFound(f"service with name {name} not found.")
        pid = service.pid  # get pid of service
        os.kill(pid, signal)

    def stop(self, name: typing.AnyStr) -> None:
        """ stop a running service """
        self.send_signal(name, SIGKILL)

    def clean_stop(self, name: typing.AnyStr) -> None:
        """Stops and also delete service files"""
        self.stop(name)
        self.clean_files(name)


__all__ = [
    "BaseObserverManager",
    "ServiceManager",
    "StartMethods"
]
