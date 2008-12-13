#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
cryo: A simple python DB persistence library.

Copyright (C) 2008  César Izurieta

This file is part of Cryo.

Cryo is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "César Izurieta"
__email__ = "cesar at caih dot org"
__version__ = "$Revision$"[11:-2]

from distutils.core import setup
import os

try:
    # Just for development to be able to do sudo python setup.py develop
    import py2app
except ImportError:
    pass

_classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
"""

examplepath = os.path.join('docs', 'example.py')
doclines = __doc__.strip().splitlines()

setup(name='cryo',
      version='0.1',
      packages=['cryo', 'cryo.backends'],
      data_files=[('docs', [examplepath])],
      maintainer='César Izurieta',
      maintainer_email='cesar@caih.org',
      url='http://code.google.com/p/cryo',
      license='http://www.gnu.org/copyleft/gpl.html',
      platforms=['unix', 'linux', 'mac', 'win'],
      description=doclines[0],
      classifiers=filter(None, _classifiers.splitlines()),
      long_description='\n'.join(doclines[2:])
)
