import os
from setuptools import setup, find_packages

VERSION = '0.9.02'

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cloud_dns_cli",
    version = VERSION,
    author = "Richard Maynard",
    author_email = "richard.maynard@gmail.com",
    url = "https://github.com/ephur/cloud_dns",
    description = ("A CLI Tool for interacting with RackSpace Cloud DNS"),
    license = "Apache 2.0",
    keywords = "rackspace cloud dns cli pyrax",
    install_requires = ['setuptools', 'pyrax>=1.6'],
    long_description=read('README.md'),
    packages = find_packages('src'),
    package_dir = {'': 'src'}, 
    entry_points= { 'console_scripts': ['cloud_dns = cloud_dns_cli.cloud_dns_cli:console'] },
    classifiers=[
				"Development Status :: 4 - Beta", 
        "Environment :: Console", 
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python", 
        "Topic :: System :: Systems Administration",
    ],
)

