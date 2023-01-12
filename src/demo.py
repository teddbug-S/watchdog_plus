
from watchdog_plus.managers import BaseObserverManager, StartMethods


# paths = [
#     ["/home/teddbug/Desktop", "desktop", False],
#     ["/home/teddbug/Downloads", "downloads", False]
# ]

items = [
    ["/home/teddbug/Desktop", 'desktop'],
    ["/home/teddbug/Downloads", 'downloads'],
]

manager = BaseObserverManager()
# configure the handler class
# it takes extra args for log_file, recursive, filter_modified
manager.handler_config(filter_modified=True, log_file="watch_log.log")

observers = manager.create_observers(items)
manager.start_observers(observers=observers)
