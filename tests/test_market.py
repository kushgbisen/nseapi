import unittest
from datetime import datetime
import os
from nseapi.market import get_market_status, download_bhavcopy, delivery_bhavcopy, bhavcopy_index

class TestNSEAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = os.path.join(os.getcwd(), 'test_downloads')
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.test_dir):
            for file in os.listdir(self.test_dir):
                os.remove(os.path.join(self.test_dir, file))
            os.rmdir(self.test_dir)

    def test_get_market_status(self):
        """Test market status retrieval."""
        response = get_market_status()
        self.assertIsInstance(response, dict, "Market status response should be a dictionary")
        self.assertIn("marketState", response, "Market status response should contain 'marketState' key")

    def test_download_bhavcopy_pre_2024(self):
        """Test bhavcopy download for pre-2024 dates."""
        date = datetime(2023, 12, 26)
        download_bhavcopy(date, download_dir=self.test_dir)
        file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        file_path = os.path.join(self.test_dir, file_name)
        
        self.assertTrue(os.path.exists(file_path), 
                        f"Bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}")
        self.assertGreater(os.path.getsize(file_path), 0, 
                           "Downloaded bhavcopy file is empty")

    def test_download_bhavcopy_2024(self):
        """Test bhavcopy download for 2024 dates."""
        date = datetime(2024, 1, 1)  # Use a more realistic date
        download_bhavcopy(date, download_dir=self.test_dir)
        file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        file_path = os.path.join(self.test_dir, file_name)
        
        self.assertTrue(os.path.exists(file_path), 
                        f"Bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}")
        self.assertGreater(os.path.getsize(file_path), 0, 
                           "Downloaded bhavcopy file is empty")

    def test_download_bhavcopy_invalid_date(self):
        """Test bhavcopy download with invalid date."""
        future_date = datetime(2025, 1, 1)
        with self.assertRaises(Exception) as context:
            download_bhavcopy(future_date, download_dir=self.test_dir)
        self.assertIn("Failed to download bhavcopy", str(context.exception))

    def test_download_delivery_bhavcopy(self):
        """Test delivery bhavcopy download."""
        date = datetime(2023, 12, 26)
        delivery_bhavcopy(date, download_dir=self.test_dir)
        file_name = f"delivery_bhavcopy_{date.strftime('%Y%m%d')}.csv"
        file_path = os.path.join(self.test_dir, file_name)
        
        self.assertTrue(os.path.exists(file_path), 
                        f"Delivery bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}")
        self.assertGreater(os.path.getsize(file_path), 0, 
                           "Downloaded delivery bhavcopy file is empty")

    def test_download_bhavcopy_index(self):
        """Test bhavcopy index download."""
        date = datetime(2023, 12, 26)
        bhavcopy_index(date, download_dir=self.test_dir)
        file_name = f"bhavcopy_index_{date.strftime('%Y%m%d')}.csv"
        file_path = os.path.join(self.test_dir, file_name)
        
        self.assertTrue(os.path.exists(file_path), 
                        f"Bhavcopy index file for {date.strftime('%Y-%m-%d')} not found at {file_path}")
        self.assertGreater(os.path.getsize(file_path), 0, 
                           "Downloaded bhavcopy index file is empty")

if __name__ == '__main__':
    unittest.main()
