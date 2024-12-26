# tests/test_core.py

import unittest
from datetime import datetime
from nseapi.core import get_market_status, download_bhavcopy
import os
import shutil

class TestNSEAPI(unittest.TestCase):

    def test_get_market_status(self):
        response = get_market_status()
        self.assertIn("marketState", response)

    def test_download_bhavcopy_pre_2024(self):
        date = datetime(2023, 12, 26)
        download_folder = 'test_downloads_pre_2024'
        download_bhavcopy(date, download_folder)
        # Correct the file path
        file_path = os.path.join(download_folder, f"cm{date.strftime('%d%b%Y').upper()}bhav.csv")
        self.assertTrue(os.path.exists(file_path))
        shutil.rmtree(download_folder)

    def test_download_bhavcopy_2024(self):
        date = datetime(2024, 12, 26)
        download_folder = 'test_downloads_2024'
        download_bhavcopy(date, download_folder)
        # Correct the file path
        file_path = os.path.join(download_folder, f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv")
        self.assertTrue(os.path.exists(file_path))
        shutil.rmtree(download_folder)

if __name__ == '__main__':
    unittest.main()
