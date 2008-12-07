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
        

if __name__ == '__main__':
    unittest.main()
