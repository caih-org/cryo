#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
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
'''

__author__ = "César Izurieta"
__email__ = "cesar at caih dot org"
__version__ = "$Revision$"[11:-2]

import unittest

from cryo import datatypes

from . import testclasses


class TableTestCase(unittest.TestCase):

    def setUp(self):
        self.tables = testclasses.gettables()

    def test_tablecreation(self):
        assert len(self.tables) == 4

        for table in self.tables:
            assert len(table.primarykey) == 1

            if table.class_ == testclasses.CompleteTestClass:
                self.assertEquals(len(table.columns), 10, table.columns)
                self.assertEquals(len(table.foreignkeys), 0, table.foreignkeys)

                for name, column in table.columns.items():
                    if isinstance(column.datatype, datatypes.Enum):
                        self.assertEquals(column.datatype.enum,
                                          testclasses.TestEnum)
                    # TODO: test all datatypes


            elif table.class_ == testclasses.ForeignKeyTestClass:
                self.assertEquals(len(table.columns), 2, table.columns)
                self.assertEquals(len(table.foreignkeys), 3, table.foreignkeys)

            elif table.class_ == testclasses.ForeignKeyTestClassOne:
                self.assertEquals(len(table.columns), 2, table.columns)
                self.assertEquals(len(table.foreignkeys), 1, table.foreignkeys)

            elif table.class_ == testclasses.ForeignKeyTestClassMany:
                self.assertEquals(len(table.columns), 3, table.columns)
                self.assertEquals(len(table.foreignkeys), 2, table.foreignkeys)

            else:
                self.fail("Table %s should not exist" % table.name)
