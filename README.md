# Watchdog Plus
A python package to built on top of [watchdog](https://github.com/gorakhargosh/watchdog) 
for extra functionality such
as monitoring multiple directory paths using processes or threads 
programmatically, easily create and schedule an observer, schedule observer services known
as WatchDogService to monitor paths in the background also providing you with APIs to 
manage the background process.

# Usage
## the Observer Manager
### Create an observer.

```python


from watchdog_plus.managers import BaseObserverManager, StartMethods

items = [
    ["/home/teddbug/Desktop", 'desktop'],
    ["/home/teddbug/Downloads", 'downloads'],
]
# initialize the manager class
manager = BaseObserverManager()
# configure the handler class
# it takes extra args for log_file and filter_modified

manager.handler_config(filter_modified=True) # handler without log file, logs to stdout
# manager.handler_config(filter_modified=True, log_file="mylogfile.log") # handler with log_file

observers = manager.create_observers(items) # create observers from items

# start a single observer
manager.start_observer(name="desktop")

# or start all the observers
manager.start_observers(observers=observers)
```
