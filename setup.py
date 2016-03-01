from setuptools import setup, find_packages
import os.path
import sys

with open("README.rst") as infile:
   readme = infile.read()
with open("CHANGES.txt") as infile:
   changes = infile.read()
long_desc = readme + '\n\n' + changes

setup(
    name='tider',
    version='1.0.0',
    description='''A correct library for dates, times and timezones.''',
    long_description=long_desc,
    keywords=['dates', 'times', 'time zones'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: PyPy",
        ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    author='Lennart Regebro',
    author_email='regebro@gmail.com',
    url="https://github.com/regebro/tider/",
    license='MIT',
    test_suite='tests'
)
