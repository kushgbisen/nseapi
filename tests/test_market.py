import unittest
from datetime import datetime
import os
import requests
from unittest import mock
from nseapi.market import (
    get_market_status,
    download_bhavcopy,
    delivery_bhavcopy,
    bhavcopy_index,
    get_corporate_actions,
    get_announcements,
    get_stock_quote,
    get_option_chain,
    get_all_indices,
)


class TestNSEAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = os.path.join(os.getcwd(), "test_downloads")
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
        self.assertIsInstance(
            response, dict, "Market status response should be a dictionary"
        )
        self.assertIn(
            "marketState",
            response,
            "Market status response should contain 'marketState' key",
        )

    def test_download_bhavcopy_pre_2024(self):
        """Test bhavcopy download for pre-2024 dates."""
        date = datetime(2023, 12, 26)
        download_bhavcopy(date, download_dir=self.test_dir)
        file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        file_path = os.path.join(self.test_dir, file_name)

        self.assertTrue(
            os.path.exists(file_path),
            f"Bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded bhavcopy file is empty"
        )

    def test_download_bhavcopy_2024(self):
        """Test bhavcopy download for 2024 dates."""
        date = datetime(2024, 1, 1)  # Use a more realistic date
        download_bhavcopy(date, download_dir=self.test_dir)
        file_name = f"BhavCopy_NSE_CM_0_0_0_{date.strftime('%Y%m%d')}_F_0000.csv"
        file_path = os.path.join(self.test_dir, file_name)

        self.assertTrue(
            os.path.exists(file_path),
            f"Bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded bhavcopy file is empty"
        )

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

        self.assertTrue(
            os.path.exists(file_path),
            f"Delivery bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded delivery bhavcopy file is empty"
        )

    def test_download_bhavcopy_index(self):
        """Test bhavcopy index download."""
        date = datetime(2023, 12, 26)
        bhavcopy_index(date, download_dir=self.test_dir)
        file_name = f"bhavcopy_index_{date.strftime('%Y%m%d')}.csv"
        file_path = os.path.join(self.test_dir, file_name)

        self.assertTrue(
            os.path.exists(file_path),
            f"Bhavcopy index file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded bhavcopy index file is empty"
        )

    def test_get_corporate_actions(self):
        """Test fetching corporate actions."""
        actions = get_corporate_actions(segment="equities")
        self.assertIsInstance(
            actions, list, "Corporate actions response should be a list"
        )
        if actions:  # Check structure if data is returned
            self.assertIn(
                "symbol", actions[0], "Corporate action should contain 'symbol' key"
            )

    def test_get_corporate_actions_with_filter(self):
        """Test fetching corporate actions with symbol and date range."""
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2023, 12, 31)
        actions = get_corporate_actions(
            segment="equities", symbol="HDFCBANK", from_date=from_date, to_date=to_date
        )
        self.assertIsInstance(
            actions, list, "Corporate actions response should be a list"
        )

    def test_get_announcements(self):
        """Test fetching corporate announcements."""
        announcements = get_announcements(index="equities")
        self.assertIsInstance(
            announcements, list, "Announcements response should be a list"
        )
        if announcements:  # Check structure if data is returned
            self.assertIn(
                "symbol", announcements[0], "Announcement should contain 'symbol' key"
            )

    def test_get_announcements_with_filter(self):
        """Test fetching corporate announcements with symbol and date range."""
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2023, 12, 31)
        announcements = get_announcements(
            index="equities", symbol="HDFCBANK", from_date=from_date, to_date=to_date
        )
        self.assertIsInstance(
            announcements, list, "Announcements response should be a list"
        )

    def test_get_stock_quote(self):
        """Test fetching stock quote for a valid symbol."""
        symbol = "INFY"
        quote = get_stock_quote(symbol)
        self.assertIsInstance(
            quote, dict, "Stock quote response should be a dictionary"
        )
        self.assertIn("symbol", quote, "Stock quote should contain 'symbol' key")
        self.assertEqual(
            quote["symbol"],
            symbol,
            "Symbol in response should match the requested symbol",
        )

    def test_get_stock_quote_invalid_symbol(self):
        """Test fetching stock quote for an invalid symbol."""
        with self.assertRaises(ValueError) as context:
            get_stock_quote("INVALID_SYMBOL")
        self.assertIn("Invalid symbol", str(context.exception))

    def test_get_option_chain_index(self):
        """Test fetching option chain for an index."""
        symbol = "NIFTY"
        option_chain = get_option_chain(symbol, is_index=True)
        self.assertIsInstance(
            option_chain, dict, "Option chain response should be a dictionary"
        )
        self.assertIn(
            "records", option_chain, "Option chain should contain 'records' key"
        )

    def test_get_option_chain_stock(self):
        """Test fetching option chain for a stock."""
        symbol = "RELIANCE"
        option_chain = get_option_chain(symbol)
        self.assertIsInstance(
            option_chain, dict, "Option chain response should be a dictionary"
        )
        self.assertIn(
            "records", option_chain, "Option chain should contain 'records' key"
        )

    def test_get_option_chain_invalid_symbol(self):
        """Test fetching option chain for an invalid symbol."""
        with self.assertRaises(ValueError) as context:
            get_option_chain("INVALID_SYMBOL")
        self.assertIn("Invalid symbol", str(context.exception))

    def test_get_all_indices(self):
        """Test fetching data for all NSE indices."""
        indices = get_all_indices()
        self.assertIsInstance(indices, list, "Indices response should be a list")
        if indices:  # Check structure if data is returned
            self.assertIn("name", indices[0], "Index data should contain 'name' key")
            self.assertIn(
                "last_price", indices[0], "Index data should contain 'last_price' key"
            )

    def test_get_all_indices_api_error(self):
        """Test handling of API errors when fetching all indices."""
        with mock.patch(
            "requests.Session.get",
            side_effect=requests.exceptions.RequestException("API error"),
        ):
            with self.assertRaises(Exception) as context:
                get_all_indices()
            self.assertIn("Failed to fetch all indices", str(context.exception))


if __name__ == "__main__":
    unittest.main()
