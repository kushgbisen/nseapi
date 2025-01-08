import unittest

from datetime import datetime, timedelta
import os
import requests
from unittest.mock import patch, Mock
import gzip

import zipfile
import shutil
from pathlib import Path
import logging
import pytest
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
    session,
    get_most_active_equities,
    get_most_active_sme,
    get_most_active_etf,
    get_volume_gainers,
    get_all_indices_performance,
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
        with patch("nseapi.fetch_data_from_nse") as mock_fetch:
            mock_fetch.return_value = {
                "CD": [{"tradingDate": "26-Jan-2025", "description": "Republic Day"}]
            }
            holidays = get_holidays(holiday_type="trading")
            self.assertIn("CD", holidays)

            self.assertEqual(holidays["CD"][0]["tradingDate"], "26-Jan-2025")
            self.assertEqual(holidays["CD"][0]["description"], "Republic Day")

    def test_get_holidays_clearing(self):
        """Test fetching clearing holidays."""

        with patch("nseapi.fetch_data_from_nse") as mock_fetch:
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

    def test_fii_dii_data(self):
        """Test fetching FII/DII trading activity data."""
        with patch("nseapi.fetch_data_from_nse") as mock_fetch:
            mock_fetch.return_value = [
                {
                    "category": "FII/FPI *",
                    "date": "07-Jan-2025",
                    "buyValue": "11726.68",
                    "sellValue": "13218.14",
                    "netValue": "-1491.46",
                },
                {
                    "category": "DII **",
                    "date": "07-Jan-2025",
                    "buyValue": "12256.43",
                    "sellValue": "10641.15",
                    "netValue": "1615.28",
                },
            ]
            data = get_fii_dii_data()
            self.assertIsInstance(data, list, "FII/DII data response should be a list")
            self.assertIn(
                "category", data[0], "FII/DII data should contain 'category' key"
            )
            self.assertIn("date", data[0], "FII/DII data should contain 'date' key")
            self.assertIn(
                "buyValue", data[0], "FII/DII data should contain 'buyValue' key"
            )
            self.assertIn(
                "sellValue", data[0], "FII/DII data should contain 'sellValue' key"
            )

            self.assertIn(
                "netValue", data[0], "FII/DII data should contain 'netValue' key"
            )

    def test_logging_setup(self):
        """Test if logger is properly configured."""
        logger.info("Test message")
        log_file = Path("logs/nseapi.log")

        self.assertTrue(log_file.exists())

        # Clean up
        for handler in logger.handlers:

            handler.close()

            logger.removeHandler(handler)
        log_file.unlink()

    def test_fetch_data_from_nse_success(self):
        """Test successful API request."""
        with patch("nseapi.session.get") as mock_get:

            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"key": "value"}
            data = fetch_data_from_nse("test-endpoint")
            self.assertEqual(data, {"key": "value"})

    def test_fetch_data_from_nse_retry(self):
        """Test retry logic on failed API request."""
        with patch(
            "nseapi.session.get",
            side_effect=requests.exceptions.RequestException("Failed"),
        ) as mock_get:
            with self.assertRaises(requests.exceptions.RequestException) as context:
                fetch_data_from_nse("test-endpoint", retries=3, delay=1)
            self.assertEqual(str(context.exception), "Failed")
            self.assertEqual(mock_get.call_count, 3)

    def test_fetch_data_from_nse_timeout(self):
        """Test timeout handling."""
        with patch(
            "nseapi.session.get", side_effect=requests.exceptions.Timeout("Timeout")
        ) as mock_get:

            with self.assertRaises(requests.exceptions.Timeout) as context:
                fetch_data_from_nse("test-endpoint", timeout=5)
            self.assertEqual(str(context.exception), "Timeout")

    def test_get_most_active_equities_volume(self):
        """Test fetching most active equities by volume."""
        mock_response = {
            "data": [
                {
                    "symbol": "IDEA",
                    "identifier": "IDEAEQN",
                    "lastPrice": 8.04,
                    "pChange": -0.24813895781639392,
                    "quantityTraded": 253738995,
                    "totalTradedVolume": 294651841,
                    "totalTradedValue": 2348375172.77,
                    "previousClose": 8.06,
                    "exDate": "20-Aug-2024",
                    "purpose": "ANNUAL GENERAL MEETING",
                    "yearHigh": 19.18,
                    "yearLow": 6.61,
                    "change": -0.02000000000000135,
                    "open": 8.08,
                    "closePrice": 0,
                    "dayHigh": 8.1,
                    "dayLow": 7.87,
                    "lastUpdateTime": "08-Jan-2025 15:59:59",
                }
            ],
            "timestamp": "08-Jan-2025 16:00:00",
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            data = get_most_active_equities("volume")
            self.assertIsInstance(data, list, "Response should be a list")

            self.assertIn("symbol", data[0], "Data should contain 'symbol' key")

    def test_get_most_active_equities_value(self):
        """Test fetching most active equities by value."""
        mock_response = {
            "data": [
                {
                    "symbol": "RELIANCE",
                    "identifier": "RELIANCEEQN",
                    "lastPrice": 1261.35,
                    "pChange": 1.6520933231252772,
                    "quantityTraded": 16989284,
                    "totalTradedVolume": 19346579,
                    "totalTradedValue": 24439178990.170002,
                    "previousClose": 1240.85,
                    "exDate": "28-Oct-2024",
                    "purpose": "BONUS 1:1",
                    "yearHigh": 1608.8,
                    "yearLow": 1201.5,
                    "change": 20.5,
                    "open": 1249,
                    "closePrice": 0,
                    "dayHigh": 1271.05,
                    "dayLow": 1245.35,
                    "lastUpdateTime": "08-Jan-2025 16:00:00",
                }
            ],
            "timestamp": "08-Jan-2025 16:00:00",
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            data = get_most_active_equities("value")
            self.assertIsInstance(data, list, "Response should be a list")

            self.assertIn("symbol", data[0], "Data should contain 'symbol' key")

    def test_get_most_active_sme_volume(self):
        """Test fetching most active SMEs by volume."""
        mock_response = {
            "data": [
                {
                    "symbol": "CELLECOR",
                    "identifier": "CELLECORSMN",
                    "lastPrice": 75.7,
                    "pChange": -2.511268512556346,
                    "totalTradedVolume": 1776000,
                    "totalTradedValue": 1404.4608,
                    "open": 78.5,
                    "dayHigh": 81.5,
                    "dayLow": 74.65,
                    "yearHigh": 81.5,
                    "yearLow": 15.04,
                    "previousClose": 77.65,
                    "purpose": None,
                    "exDate": None,
                }
            ],
            "timestamp": "08-Jan-2025 16:00:00",
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            data = get_most_active_sme("volume")
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertIn("symbol", data[0], "Data should contain 'symbol' key")

    def test_get_most_active_sme_value(self):
        """Test fetching most active SMEs by value."""
        mock_response = {
            "data": [
                {
                    "symbol": "DANISH",
                    "identifier": "DANISHSMN",
                    "lastPrice": 1183,
                    "pChange": 0.7365776812704979,
                    "totalTradedVolume": 106200,
                    "totalTradedValue": 1251.26964,
                    "open": 1175.8,
                    "dayHigh": 1198.95,
                    "dayLow": 1150,
                    "yearHigh": 1316,
                    "yearLow": 541.5,
                    "previousClose": 1174.35,
                    "purpose": None,
                    "exDate": None,
                }
            ],
            "timestamp": "08-Jan-2025 16:00:00",
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            data = get_most_active_sme("value")
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertIn("symbol", data[0], "Data should contain 'symbol' key")

    def test_get_most_active_etf_volume(self):
        """Test fetching most active ETFs by volume."""
        mock_response = {
            "navDate": "07-Jan-2025",
            "data": [
                {
                    "symbol": "AXISBPSETF",
                    "identifier": "AXISBPSETFEQN",
                    "lastPrice": 12.26,
                    "pChange": -0.48701298701299106,
                    "totalTradedVolume": 22823585,
                    "totalTradedValue": 2789.042087,
                    "nav": 12.3031,
                    "open": 12.35,
                    "dayHigh": 12.35,
                    "dayLow": 12.21,
                    "closePrice": 0,
                    "previousClose": 12.32,
                }
            ],
            "timestamp": "08-Jan-2025 16:00:00",
            "navData": {
                "NIFTYBEES": 264.7357,
                "BANKNIFTY1": 515.9524,
            },
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            data = get_most_active_etf("volume")
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertIn("symbol", data[0], "Data should contain 'symbol' key")

    def test_get_most_active_etf_value(self):
        """Test fetching most active ETFs by value."""
        mock_response = {
            "navDate": "07-Jan-2025",
            "data": [
                {
                    "symbol": "NIFTYBEES",
                    "identifier": "NIFTYBEESEQN",
                    "lastPrice": 264.91,
                    "pChange": -0.09428269723940262,
                    "totalTradedVolume": 5056466,
                    "totalTradedValue": 13347.553300200003,
                    "nav": 264.7357,
                    "open": 265.95,
                    "dayHigh": 266.04,
                    "dayLow": 262.8,
                    "closePrice": 0,
                    "previousClose": 265.16,
                }
            ],
            "timestamp": "08-Jan-2025 16:00:00",
            "navData": {
                "NIFTYBEES": 264.7357,
                "BANKNIFTY1": 515.9524,
            },
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            data = get_most_active_etf("value")
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertIn("symbol", data[0], "Data should contain 'symbol' key")

    def test_get_volume_gainers(self):
        """Test fetching volume gainers."""
        mock_response = {
            "data": [
                {
                    "symbol": "AXISBPSETF",
                    "companyName": "AXIS MUTUAL FUND - Axis Nifty AAA Bond Plus SDL Apr 2026 50-50 ETF",
                    "volume": 22823585,
                    "week1AvgVolume": 351455,
                    "week1volChange": 64.94027684909875,
                    "week2AvgVolume": 222491,
                    "week2volChange": 102.58201339289526,
                    "ltp": 12.26,
                    "pChange": -0.49,
                    "turnover": 2789.04208,
                }
            ],
            "timestamp": "08-Jan-2025 16:00:24",
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            data = get_volume_gainers()
            self.assertIsInstance(data, list, "Response should be a list")
            self.assertIn("symbol", data[0], "Data should contain 'symbol' key")

    def test_get_regulatory_status(self):
        """Test fetching regulatory module status."""
        mock_response = {
            "data": {
                "preopen_data_list": "true",
                "niftynxt": "true",
            }
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):
            status = get_regulatory_status()
            self.assertIsInstance(status, dict, "Response should be a dictionary")

            self.assertIn("data", status, "Response should contain 'data' key")

    def test_get_all_indices_performance(self):
        """Test fetching performance data for all indices."""
        mock_response = {
            "data": [
                {
                    "key": "BROAD MARKET INDICES",
                    "index": "NIFTY 50",

                    "indexSymbol": "NIFTY 50",
                    "last": 23688.95,
                    "variation": -18.95,
                    "percentChange": -0.08,
                    "open": 23746.65,
                    "high": 23751.85,
                    "low": 23496.15,
                    "previousClose": 23707.9,
                    "yearHigh": 26277.35,
                    "yearLow": 21137.2,
                    "indicativeClose": 0,
                    "pe": "21.83",
                    "pb": "3.53",
                    "dy": "1.27",
                    "declines": "28",
                    "advances": "22",
                    "unchanged": "1",
                    "perChange365d": 10.11,
                    "date365dAgo": "08-Jan-2024",
                    "chart365dPath": "https://nsearchives.nseindia.com/365d/NIFTY-50.svg",
                    "date30dAgo": "06-Dec-2024",
                    "perChange30d": -4.01,
                    "chart30dPath": "https://nsearchives.nseindia.com/30d/NIFTY-50.svg",
                    "chartTodayPath": "https://nsearchives.nseindia.com/today/NIFTY-50.svg",

                    "previousDay": 23616.05,
                    "oneWeekAgo": 23742.9,
                    "oneMonthAgo": 24677.8,

                    "oneYearAgo": 21513,

                }
            ],
            "timestamp": "08-Jan-2025 15:30",
            "advances": 2215,

            "declines": 5649,
            "unchanged": 71,
            "dates": {
                "previousDay": "06-Jan-2025",
                "oneWeekAgo": "01-Jan-2025",

                "oneMonthAgo": "06-Dec-2024",

                "oneYearAgo": "08-Jan-2024",
            },
            "date30dAgo": "06-Dec-2024",
            "date365dAgo": "08-Jan-2024",
        }

        with patch("nseapi.fetch_data_from_nse", return_value=mock_response):

            data = get_all_indices_performance()


            self.assertIsInstance(data, dict, "Response should be a dictionary")
            self.assertIn("data", data, "Response should contain 'data' key")
            self.assertIn("timestamp", data, "Response should contain 'timestamp' key")

if __name__ == "__main__":

    unittest.main()
