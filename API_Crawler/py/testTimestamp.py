import unittest
from timestamp import Timestamp

class testTimestamp(unittest.TestCase):

    def test_get_date_now(self):
        result = Timestamp().get_date_now()
        self.assertEqual(result, "2021-04-19")

    def test_format_date(self):
        result = Timestamp().format_date("1998-12-08")
        self.assertEqual(result, "19981208")
    
    def test_timerange(self):
        result = Timestamp().timerange("2021-04-16", "2021-04-19")
        self.assertEqual(result, ["2021-04-16", "2021-04-17", "2021-04-18", "2021-04-19"])

if __name__ == "__main__":
    unittest.main()