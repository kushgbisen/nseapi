import unittest
from datetime import datetime
from src.market import get_market_status, download_bhavcopy
import os

class TestNSEAPI(unittest.TestCase):

    def test_get_market_status(self):
        response = get_market_status()
        self.assertIn("marketState", response, "Market status response does not contain 'marketState' key")
        print("✅ Market status test passed")

    def test_download_bhavcopy_pre_2024(self):
        date = datetime(2023, 12, 26)
        download_bhavcopy(date)
        file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        file_path = os.path.join(os.getcwd(), file_name)
        self.assertTrue(os.path.exists(file_path), f"Bhavcopy file for {date.strftime('%Y-%m-%d')} does not exist at {file_path}")
        print(f"✅ Bhavcopy download test for {date.strftime('%Y-%m-%d')} passed")
        os.remove(file_path)  # Clean up the downloaded file

    def test_download_bhavcopy_2024(self):
        date = datetime(2024, 12, 26)
        download_bhavcopy(date)
        file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        file_path = os.path.join(os.getcwd(), file_name)
        self.assertTrue(os.path.exists(file_path), f"Bhavcopy file for {date.strftime('%Y-%m-%d')} does not exist at {file_path}")
        print(f"✅ Bhavcopy download test for {date.strftime('%Y-%m-%d')} passed")
        os.remove(file_path)  # Clean up the downloaded file

if __name__ == '__main__':
    unittest.main()
