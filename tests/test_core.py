# tests/test_core.py

import unittest
from nseapi.utils import fetch_data_from_nse

class TestNSEAPI(unittest.TestCase):

    def test_fetch_data_from_nse(self):
        endpoint = "marketStatus"
        response = fetch_data_from_nse(endpoint)
        self.assertIn("marketState", response)

if __name__ == '__main__':
    unittest.main()
