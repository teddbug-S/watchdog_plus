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



"""
Exceptions for watchdog observers
================================
"""


# base exception class
class WatchDogPlusError(Exception):
    ...


# raised when retrieving a service or an observer is not successful
class DoesNotExist(WatchDogPlusError):
    ...


# raised when two observers or services have the same name
class AlreadyExists(WatchDogPlusError):
    ...


"""
Exceptions for services
===========================
"""


# base class for all exceptions raised by a service
class WatchdogServiceError(Exception):
    ...


# raised when service pid can't be returned
class ServicePIDNotFound(WatchdogServiceError):
    ...


# raised when service pid can't be returned
class ServiceNotRunning(WatchdogServiceError):
    ...


# raised when service file not found during a service reload
class ServiceReloadError(WatchdogServiceError):
    ...


# raised when no services found
class ServiceNotFound(WatchDogPlusError):
    ...


__all__ = [
    "WatchDogPlusError",
    "AlreadyExists",
    "DoesNotExist",
    "ServiceNotFound",
    "ServiceNotRunning",
    "ServicePIDNotFound",
    "ServiceReloadError",
]
