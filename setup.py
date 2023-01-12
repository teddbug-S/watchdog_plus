from setuptools import setup, find_packages


with open("README.md") as f:
    long_description = f.read()

# dependencies
requires = ["watchdog"]

description = """
A python package to built on top of [watchdog](https://github.com/gorakhargosh/watchdog) 
for extra functionality such
as monitoring multiple directory paths using processes or threads 
programmatically, easily create and schedule an observer, schedule observer services known
as WatchDogService to monitor paths in the background also providing you with APIs to 
manage the background process.
"""

setup(
    name="watchdog_plus",
    version="3.0.0",
    author="Divine Darkey (teddbug-S)",
    author_email="etornam47@protonmail.com",
    maintainer="Divine Darkey",
    maintainer_email="etornam47@protonmail.com",
    requires=requires,
    description=description,
    long_description=long_description,
    packages=find_packages("watchdog_plus"),
)
