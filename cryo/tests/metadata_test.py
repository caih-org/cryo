import unittest

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

                for column in table.columns:
                    pass

                assert len(table.foreignkeys) == 0


            elif table.class_ == testclasses.ForeignKeyTestClass:
                self.assertEquals(len(table.columns), 2, table.columns)
                self.assertEquals(len(table.foreignkeys), 2, table.foreignkeys)

            elif table.class_ == testclasses.ForeignKeyTestClassOne:
                self.assertEquals(len(table.columns), 2, table.columns)
                self.assertEquals(len(table.foreignkeys), 1, table.foreignkeys)

            elif table.class_ == testclasses.ForeignKeyTestClassMany:
                self.assertEquals(len(table.columns), 2, table.columns)
                self.assertEquals(len(table.foreignkeys), 1, table.foreignkeys)

            else:
                self.fail("Table %s should not exist" % table.name)
        

if __name__ == '__main__':
    unittest.main()
