import unittest
from datetime import datetime, timedelta
import os
import requests
from unittest.mock import patch
from pathlib import Path
import logging
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

    get_fii_dii_data,
    get_top_gainers,
    get_top_losers,
    get_regulatory_status,
    fetch_data_from_nse,
    logger,
    get_most_active_equities,
    get_most_active_sme,

    get_most_active_etf,
    get_volume_gainers,
    get_all_indices_performance,

    get_price_band_hitters,
    get_52_week_high,
    get_52_week_low,
    get_52_week_counts,
    get_52_week_data_by_symbol,  # New function
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


    # Helper method to mock API responses
    def mock_fetch_data(self, mock_response):
        return patch("nseapi.fetch_data_from_nse", return_value=mock_response)

    # Market Status

    def test_get_market_status(self):
        with self.mock_fetch_data({"marketState": "Open"}):
            response = get_market_status()
            self.assertIsInstance(response, dict)
            self.assertIn("marketState", response)

    # Bhavcopy Tests
    def test_get_bhavcopy_equity(self):
        date = datetime(2023, 12, 26)
        with patch("nseapi.fetch_data_from_nse", return_value=b"mock_data"):

            file_path = get_bhavcopy("equity", date, download_dir=self.test_dir)
            self.assertTrue(os.path.exists(file_path))
            self.assertGreater(os.path.getsize(file_path), 0)


    def test_get_bhavcopy_delivery(self):
        date = datetime(2023, 12, 26)
        with patch("nseapi.fetch_data_from_nse", return_value=b"mock_data"):
            file_path = get_bhavcopy("delivery", date, download_dir=self.test_dir)
            self.assertTrue(os.path.exists(file_path))
            self.assertGreater(os.path.getsize(file_path), 0)

    def test_get_bhavcopy_indices(self):

        date = datetime(2023, 12, 26)
        with patch("nseapi.fetch_data_from_nse", return_value=b"mock_data"):
            file_path = get_bhavcopy("indices", date, download_dir=self.test_dir)
            self.assertTrue(os.path.exists(file_path))

            self.assertGreater(os.path.getsize(file_path), 0)

    def test_get_bhavcopy_fno(self):
        date = datetime(2024, 12, 26)

        with patch("nseapi.fetch_data_from_nse", return_value=b"mock_data"):
            file_path = get_bhavcopy("fno", date, download_dir=self.test_dir)
            self.assertTrue(os.path.exists(file_path))
            self.assertGreater(os.path.getsize(file_path), 0)


    def test_get_bhavcopy_priceband(self):
        date = datetime(2023, 12, 26)

        with patch("nseapi.fetch_data_from_nse", return_value=b"mock_data"):
            file_path = get_bhavcopy("priceband", date, download_dir=self.test_dir)
            self.assertTrue(os.path.exists(file_path))

            self.assertGreater(os.path.getsize(file_path), 0)

    def test_get_bhavcopy_pr(self):
        date = datetime(2023, 12, 26)
        with patch("nseapi.fetch_data_from_nse", return_value=b"mock_data"):
            file_path = get_bhavcopy("pr", date, download_dir=self.test_dir)
            self.assertTrue(os.path.exists(file_path))
            self.assertGreater(os.path.getsize(file_path), 0)

    def test_get_bhavcopy_cm_mii(self):
        date = datetime(2025, 1, 2)
        with patch("nseapi.fetch_data_from_nse", return_value=b"mock_data"):
            file_path = get_bhavcopy("cm_mii", date, download_dir=self.test_dir)
            self.assertTrue(os.path.exists(file_path))

            self.assertGreater(os.path.getsize(file_path), 0)

    def test_get_bhavcopy_invalid_type(self):

        date = datetime(2023, 12, 26)
        with self.assertRaises(ValueError) as context:
            get_bhavcopy("invalid_type", date, download_dir=self.test_dir)
        self.assertIn("Invalid bhavcopy_type", str(context.exception))


    # Corporate Actions

    def test_get_corporate_actions(self):
        with self.mock_fetch_data([{"symbol": "HDFCBANK", "action": "Dividend"}]):
            actions = get_corporate_actions(segment="equities")
            self.assertIsInstance(actions, list)

            if actions:
                self.assertIn("symbol", actions[0])

    def test_get_corporate_actions_with_filter(self):
        from_date = datetime(2023, 1, 1)
        to_date = datetime(2023, 12, 31)
        with self.mock_fetch_data([{"symbol": "HDFCBANK", "action": "Dividend"}]):
            actions = get_corporate_actions(
                segment="equities", symbol="HDFCBANK", from_date=from_date, to_date=to_date
            )
            self.assertIsInstance(actions, list)

    # Corporate Announcements
    def test_get_announcements(self):
        with self.mock_fetch_data([{"symbol": "HDFCBANK", "announcement": "Dividend"}]):
            announcements = get_announcements(index="equities")
            self.assertIsInstance(announcements, list)

            if announcements:
                self.assertIn("symbol", announcements[0])

    def test_get_announcements_with_filter(self):

        from_date = datetime(2023, 1, 1)
        to_date = datetime(2023, 12, 31)
        with self.mock_fetch_data([{"symbol": "HDFCBANK", "announcement": "Dividend"}]):
            announcements = get_announcements(
                index="equities", symbol="HDFCBANK", from_date=from_date, to_date=to_date

            )
            self.assertIsInstance(announcements, list)

    # Stock Quotes
    def test_get_stock_quote(self):
        with self.mock_fetch_data({"info": {"symbol": "INFY"}, "priceInfo": {"lastPrice": 1500}}):
            quote = get_stock_quote("INFY")
            self.assertIsInstance(quote, dict)
            self.assertEqual(quote["symbol"], "INFY")

    def test_get_stock_quote_invalid_symbol(self):
        with self.mock_fetch_data(None):
            with self.assertRaises(ValueError) as context:
                get_stock_quote("INVALID_SYMBOL")
            self.assertIn("Invalid symbol", str(context.exception))

    # Option Chain
    def test_get_option_chain(self):
        with self.mock_fetch_data({"records": {"data": []}}):
            option_chain = get_option_chain("RELIANCE")
            self.assertIsInstance(option_chain, dict)

            self.assertIn("records", option_chain)

    def test_get_option_chain_index(self):
        with self.mock_fetch_data({"records": {"data": []}}):
            option_chain = get_option_chain("NIFTY", is_index=True)
            self.assertIsInstance(option_chain, dict)
            self.assertIn("records", option_chain)


    def test_get_option_chain_invalid_symbol(self):
        with self.mock_fetch_data(None):
            with self.assertRaises(ValueError) as context:
                get_option_chain("INVALID_SYMBOL")
            self.assertIn("Invalid symbol", str(context.exception))

    # Indices
    def test_get_all_indices(self):
        with self.mock_fetch_data({"data": [{"index": "NIFTY 50", "last": 18000}]}):
            indices = get_all_indices()

            self.assertIsInstance(indices, list)
            if indices:
                self.assertIn("name", indices[0])

    # Holidays
    def test_get_holidays_trading(self):
        with self.mock_fetch_data({"CD": [{"tradingDate": "26-Jan-2025", "description": "Republic Day"}]}):
            holidays = get_holidays(holiday_type="trading")

            self.assertIn("CD", holidays)

    def test_get_holidays_clearing(self):

        with self.mock_fetch_data({"CD": [{"tradingDate": "19-Feb-2025", "description": "Chhatrapati Shivaji Maharaj Jayanti"}]}):
            holidays = get_holidays(holiday_type="clearing")

            self.assertIn("CD", holidays)

    # Bulk Deals
    def test_bulk_deals(self):
        from_date = datetime(2023, 1, 1)

        to_date = datetime(2023, 12, 31)
        with self.mock_fetch_data([{"symbol": "RELIANCE", "quantity": 1000}]):
            bulk_deals_data = bulk_deals(from_date, to_date)
            self.assertIsInstance(bulk_deals_data, list)


    # FII/DII Data
    def test_get_fii_dii_data(self):
        with self.mock_fetch_data([{"category": "FII/FPI", "netValue": "-1491.46"}]):
            data = get_fii_dii_data()

            self.assertIsInstance(data, list)
            if data:
                self.assertIn("category", data[0])

    # Top Gainers/Losers

    def test_get_top_gainers(self):
        with self.mock_fetch_data([{"symbol": "RELIANCE", "pChange": 5.0}]):
            top_gainers = get_top_gainers()
            self.assertIsInstance(top_gainers, list)

    def test_get_top_losers(self):

        with self.mock_fetch_data([{"symbol": "INFY", "pChange": -3.0}]):

            top_losers = get_top_losers()
            self.assertIsInstance(top_losers, list)

    # Regulatory Status
    def test_get_regulatory_status(self):
        with self.mock_fetch_data({"data": {"preopen_data_list": "true"}}):
            status = get_regulatory_status()
            self.assertIsInstance(status, dict)


    # Most Active Securities
    def test_get_most_active_equities(self):
        with self.mock_fetch_data({"data": [{"symbol": "RELIANCE", "volume": 100000}]}):
            data = get_most_active_equities("volume")
            self.assertIsInstance(data, list)

    def test_get_most_active_sme(self):
        with self.mock_fetch_data({"data": [{"symbol": "SME", "volume": 50000}]}):
            data = get_most_active_sme("volume")

            self.assertIsInstance(data, list)

    def test_get_most_active_etf(self):

        with self.mock_fetch_data({"data": [{"symbol": "ETF", "volume": 20000}]}):
            data = get_most_active_etf("volume")
            self.assertIsInstance(data, list)

    # Volume Gainers
    def test_get_volume_gainers(self):
        with self.mock_fetch_data({"data": [{"symbol": "INFY", "volume": 200000}]}):
            data = get_volume_gainers()
            self.assertIsInstance(data, list)

    # Price Band Hitters
    def test_get_price_band_hitters(self):
        with self.mock_fetch_data({"upper": {"AllSec": {"data": [{"symbol": "RELIANCE"}]}}}):
            result = get_price_band_hitters(band_type="upper", category="AllSec")
            self.assertIsInstance(result, dict)


    # 52-Week High/Low Data
    def test_get_52_week_high(self):
        with self.mock_fetch_data({"data": [{"symbol": "INFY", "yearHigh": "2006.45"}]}):
            result = get_52_week_high()
            self.assertIsInstance(result, dict)

            self.assertIn("data", result)

    def test_get_52_week_low(self):
        with self.mock_fetch_data({"data": [{"symbol": "INFY", "yearLow": "1358.35"}]}):
            result = get_52_week_low()
            self.assertIsInstance(result, dict)
            self.assertIn("data", result)

    def test_get_52_week_counts(self):
        with self.mock_fetch_data({"high": 54, "low": 73}):
            result = get_52_week_counts()
            self.assertIsInstance(result, dict)
            self.assertIn("high", result)
            self.assertIn("low", result)

    # New Feature: 52-Week High/Low Data for a Specific Symbol

    def test_get_52_week_data_by_symbol(self):
        mock_response = [
            {

                "symbol": "INFY",
                "series": "EQ",
                "markettype": "N",
                "CompanyName": "Infosys Limited",
                "ltp": "1932.75",
                "secStatus": "Listed",
                "yearHigh": "2006.45 (13-Dec-2024)",
                "yearHighDt": "13-Dec-2024",
                "yearLow": "1358.35 (04-Jun-2024)",
                "yearLowDt": "04-Jun-2024",
            }
        ]

        with self.mock_fetch_data(mock_response):
            result = get_52_week_data_by_symbol("INFY")
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["symbol"], "INFY")
            self.assertEqual(result[0]["yearHigh"], "2006.45 (13-Dec-2024)")
            self.assertEqual(result[0]["yearLow"], "1358.35 (04-Jun-2024)")


    def test_get_52_week_data_by_symbol_invalid_symbol(self):
        with self.mock_fetch_data([]):
            with self.assertRaises(ValueError) as context:
                get_52_week_data_by_symbol("INVALID_SYMBOL")
            self.assertIn("No data found for symbol", str(context.exception))

    def test_get_52_week_data_by_symbol_api_error(self):
        with patch("nseapi.fetch_data_from_nse", side_effect=requests.exceptions.RequestException("API Error")):
            with self.assertRaises(Exception) as context:
                get_52_week_data_by_symbol("INFY")
            self.assertIn("API request failed", str(context.exception))



if __name__ == "__main__":
    unittest.main()
