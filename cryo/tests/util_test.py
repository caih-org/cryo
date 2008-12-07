import unittest
import doctest

from .. import util


class UtilTest():#(unittest.TestCase):

    def test_doctest(self):
        doctest.testmod(util)
