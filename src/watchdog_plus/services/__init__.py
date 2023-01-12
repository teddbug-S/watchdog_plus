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


import os
import typing
import shlex
from subprocess import run

from ..errors import ServicePIDNotFound


# Defining some helper classes
class ReadOnlyProperty(object):
    """A simple descriptor to make some properties readonly"""

    def __set_name__(self, owner, name):
        self.owner = owner
        self.name = name

    def __set__(self, obj, value):
        raise AttributeError("attribute is readonly.")


#  subclass of ReadOnlyProperty
class ServiceName(ReadOnlyProperty):
    """
    A special field to keep the name of a service unaltered.
    This is because changing the name of a service implies recreating
    the service since its name is used in launch command etc.
    """

    # return the provided name
    def __get__(self, obj, obj_type):
        return getattr(obj, "__name")


# another subclass of ReadOnlyProperty
class HiddenReadOnly(ReadOnlyProperty):
    """
    A readonly field for hidden or restricted access properties
    """

    # get a hidden value from the class
    def __get__(self, obj, obj_type):
        result = getattr(obj, f"_{self.owner.__name__}__get_{self.name}")
        return result()


class WatchDogPlusService:
    name = ServiceName()
    pid = HiddenReadOnly()
    launch_command = HiddenReadOnly()

    def __init__(self, path: typing.AnyStr, name: typing.AnyStr, service_dir: typing.AnyStr = None) -> None:
        # hidden properties
        self.__name = name
        self.service_dir = service_dir if service_dir else f"{self.name} watchdog-service"  # type: ignore
        try:
            os.mkdir(self.service_dir)
        except FileExistsError:
            ...  # just pass

        self.path = path
        self.is_active = False

    def __get_launch_command(self) -> str:
        """Command used to launch service"""
        command = " ".join(
            [
                "nohup",  # disables hang up signals sent to service file
                "python3",  # python3
                "-u",  # force the stdout and stderr streams to be unbuffered
                f"{shlex.quote(self.service_file)}",
                f" > {shlex.quote(self.output_file)} &",
            ]
        )
        return command

    def __get_pid(self) -> int:
        """Returns pid of service"""
        # initialise command
        command = shlex.join(["ps", "-fU", shlex.quote(os.environ["USER"])])
        output = run(command, text=True, capture_output=True, shell=True).stdout
        # search for the process
        pattern = f"python3 -u ./{self.name.lower()}_service"
        try:
            match = [line for line in output.splitlines() if pattern in line][0]
            pid = int(match.split()[1])
        except (IndexError, ValueError):
            raise ServicePIDNotFound(
                f"the pid of service {self.name.lower()!r} not found, is it running?"
            )
        else:
            return pid

    @property
    def service_file(self) -> typing.AnyStr:
        """generates a service file"""
        file_name = os.path.join(
            self.service_dir,  # type: ignore
            "{}_service.py"  # type: ignore
        )
        return file_name.format(shlex.quote(self.name.lower()))

    @property
    def output_file(self) -> typing.AnyStr:
        """generates an output file"""
        file_name = os.path.join(
            self.service_dir,  # type: ignore
            "{}_output.txt"  # type: ignore
        )
        return file_name.format(shlex.quote(self.name.lower()))


__all__ = ["WatchDogPlusService"]
