#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='piu',
    version='0.1.0',
    description='Pdf images extract library',
    long_description=readme + '\n\n' + history,
    author='Krazy Lee',
    author_email='lixiangstar@gmail.com',
    url='https://github.com/Krazylee/piu',
    packages=[
        'piu',
    ],
    package_dir={'piu': 'piu'},
    include_package_data=True,
    install_requires=[
        "ghostscript"
    ],
    license="BSD",
    zip_safe=False,
    keywords='travel',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    cmdclass = {'test': PyTest},
    test_suite='tests',
)
