import unittest
from sqlalchemy import types as sqltypes
from pyavrio.sqlalchemy.datatype import DOUBLE, MAP, ROW, TIME, TIMESTAMP, parse_sqltype  

class TestParseSQLType(unittest.TestCase):

    def test_basic_types(self):
        # Test for basic types
        self.assertIsInstance(parse_sqltype('integer'), sqltypes.INTEGER)
        self.assertIsInstance(parse_sqltype('varchar'), sqltypes.VARCHAR)
        self.assertIsInstance(parse_sqltype('boolean'), sqltypes.BOOLEAN)
        self.assertIsInstance(parse_sqltype('double'), DOUBLE)
    
    def test_array_type(self):
        result = parse_sqltype('array(integer)')
        self.assertIsInstance(result, sqltypes.ARRAY)
        self.assertEqual(result.item_type.__class__, sqltypes.INTEGER) 

    def test_map_type(self):
        result = parse_sqltype('map(integer, varchar)')
        self.assertIsInstance(result, MAP)
        self.assertEqual(result.key_type.__class__, sqltypes.INTEGER) 
        self.assertEqual(result.value_type.__class__, sqltypes.VARCHAR)  

    def test_row_type(self):
        result = parse_sqltype('row("name" varchar, "age" integer)')
        self.assertIsInstance(result, ROW)
        self.assertEqual(len(result.attr_types), 2)
        self.assertEqual(result.attr_types[0][0], "name")
        self.assertEqual(result.attr_types[0][1].__class__, sqltypes.VARCHAR) 
        self.assertEqual(result.attr_types[1][0], "age")
        self.assertEqual(result.attr_types[1][1].__class__, sqltypes.INTEGER)  

    def test_unrecognized_type(self):
        result = parse_sqltype('unknown_type')
        self.assertEqual(result, sqltypes.NULLTYPE)

    def test_time_types(self):
        result = parse_sqltype('time')
        self.assertIsInstance(result, TIME)

        result = parse_sqltype('timestamp')
        self.assertIsInstance(result, TIMESTAMP)

    def test_type_with_precision(self):
        result = parse_sqltype('timestamp(3)')
        self.assertIsInstance(result, TIMESTAMP)
        self.assertEqual(result.precision, 3)

if __name__ == '__main__':
    unittest.main()