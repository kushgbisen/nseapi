# tests/test_core.py

import unittest
from nseapi.core import get_market_status

class TestNSEAPI(unittest.TestCase):

    def test_get_market_status(self):
        response = get_market_status()
        self.assertIn("marketState", response)

if __name__ == '__main__':
    unittest.main()
