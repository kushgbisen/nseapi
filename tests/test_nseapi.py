import unittest
from datetime import datetime, timedelta
import os
import requests
from unittest.mock import patch, Mock
import gzip
import zipfile
import shutil
from nseapi import (
    get_market_status,
    get_bhavcopy,
    get_corporate_actions,
    get_announcements,
    get_stock_quote,
    get_option_chain,
    get_all_indices,
    get_holidays,
    bulk_deals,
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

    def test_get_bhavcopy_equity(self):
        """Test equity bhavcopy download."""
        date = datetime(2023, 12, 26)
        file_path = get_bhavcopy("equity", date, download_dir=self.test_dir)
        self.assertTrue(
            os.path.exists(file_path),
            f"Equity bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded equity bhavcopy file is empty"
        )

    def test_get_bhavcopy_delivery(self):
        """Test delivery bhavcopy download."""
        date = datetime(2023, 12, 26)
        file_path = get_bhavcopy("delivery", date, download_dir=self.test_dir)

        self.assertTrue(
            os.path.exists(file_path),
            f"Delivery bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded delivery bhavcopy file is empty"
        )

    def test_get_bhavcopy_indices(self):
        """Test indices bhavcopy download."""
        date = datetime(2023, 12, 26)

        file_path = get_bhavcopy("indices", date, download_dir=self.test_dir)

        self.assertTrue(
            os.path.exists(file_path),
            f"Indices bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded indices bhavcopy file is empty"
        )

    def test_get_bhavcopy_fno(self):
        """Test FnO bhavcopy download."""
        date = datetime(2024, 12, 26)

        file_path = get_bhavcopy("fno", date, download_dir=self.test_dir)
        self.assertTrue(
            os.path.exists(file_path),
            f"FnO bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded FnO bhavcopy file is empty"
        )

    def test_get_bhavcopy_priceband(self):
        """Test priceband report download."""
        date = datetime(2023, 12, 26)
        file_path = get_bhavcopy("priceband", date, download_dir=self.test_dir)
        self.assertTrue(
            os.path.exists(file_path),
            f"Priceband report file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded priceband report file is empty"
        )

    def test_get_bhavcopy_pr(self):
        """Test PR bhavcopy download."""
        date = datetime(2023, 12, 26)
        file_path = get_bhavcopy("pr", date, download_dir=self.test_dir)
        self.assertTrue(
            os.path.exists(file_path),
            f"PR bhavcopy file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path), 0, "Downloaded PR bhavcopy file is empty"
        )

    def test_get_bhavcopy_cm_mii(self):
        """Test CM MII security report download."""
        date = datetime(2025, 1, 2)
        file_path = get_bhavcopy("cm_mii", date, download_dir=self.test_dir)
        self.assertTrue(
            os.path.exists(file_path),
            f"CM MII security report file for {date.strftime('%Y-%m-%d')} not found at {file_path}",
        )
        self.assertGreater(
            os.path.getsize(file_path),
            0,
            "Downloaded CM MII security report file is empty",
        )

    def test_get_bhavcopy_invalid_type(self):
        """Test get_bhavcopy with invalid bhavcopy type."""
        date = datetime(2023, 12, 26)
        with self.assertRaises(ValueError) as context:
            get_bhavcopy("invalid_type", date, download_dir=self.test_dir)

        self.assertIn("Invalid bhavcopy_type", str(context.exception))

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
            self.assertIn(
                "change", indices[0], "Index data should contain 'change' key"
            )

            self.assertIn(
                "percent_change",
                indices[0],
                "Index data should contain 'percent_change' key",
            )

    def test_get_holidays_trading(self):
        """Test fetching trading holidays."""
        with patch("nseapi.helpers.fetch_data_from_nse") as mock_fetch:
            mock_fetch.return_value = {
                "CD": [{"tradingDate": "26-Jan-2025", "description": "Republic Day"}]
            }
            holidays = get_holidays(holiday_type="trading")
            self.assertIn("CD", holidays)
            self.assertEqual(holidays["CD"][0]["tradingDate"], "26-Jan-2025")
            self.assertEqual(holidays["CD"][0]["description"], "Republic Day")

    def test_get_holidays_clearing(self):
        """Test fetching clearing holidays."""
        with patch("nseapi.helpers.fetch_data_from_nse") as mock_fetch:

            mock_fetch.return_value = {
                "CD": [
                    {
                        "tradingDate": "19-Feb-2025",
                        "description": "Chhatrapati Shivaji Maharaj Jayanti",
                    }
                ]
            }
            holidays = get_holidays(holiday_type="clearing")

            self.assertIn("CD", holidays)
            self.assertEqual(holidays["CD"][0]["tradingDate"], "19-Feb-2025")

            self.assertEqual(
                holidays["CD"][0]["description"], "Chhatrapati Shivaji Maharaj Jayanti"
            )

    def test_bulk_deals(self):
        """Test fetching bulk deals."""
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2023, 12, 31)
        bulk_deals_data = bulk_deals(from_date, to_date)
        self.assertIsInstance(
            bulk_deals_data, list, "Bulk deals response should be a list"
        )


if __name__ == "__main__":
    unittest.main()
