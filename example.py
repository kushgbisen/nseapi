from datetime import datetime
from nseapi import (
    get_market_status,
    get_bhavcopy,
    get_stock_quote,
    get_option_chain,
    get_all_indices,
    get_corporate_actions,
    get_announcements,
    get_holidays,
    bulk_deals,
    get_fii_dii_data,
    get_top_gainers,
    get_top_losers,
    get_regulatory_status,
)

def main():
    # Test get_market_status
    print("=== Testing get_market_status ===")
    market_status = get_market_status()
    print("Market Status:", market_status)
    print("\n")

    # Test get_bhavcopy (equity)
    print("=== Testing get_bhavcopy (equity) ===")
    date = datetime(2023, 12, 26)
    try:
        bhavcopy_path = get_bhavcopy("equity", date, download_dir="downloads")
        print(f"Bhavcopy downloaded to: {bhavcopy_path}")

    except Exception as e:
        print(f"Failed to download bhavcopy: {e}")
    print("\n")

    # Test get_stock_quote
    print("=== Testing get_stock_quote ===")
    symbol = "INFY"

    try:
        stock_quote = get_stock_quote(symbol)
        print(f"Stock Quote for {symbol}: {stock_quote}")
    except Exception as e:

        print(f"Failed to fetch stock quote: {e}")
    print("\n")

    # Test get_option_chain (stock)
    print("=== Testing get_option_chain (stock) ===")
    symbol = "RELIANCE"
    try:
        option_chain = get_option_chain(symbol)
        print(f"Option Chain for {symbol}: {option_chain}")
    except Exception as e:
        print(f"Failed to fetch option chain: {e}")
    print("\n")

    # Test get_option_chain (index)
    print("=== Testing get_option_chain (index) ===")
    symbol = "NIFTY"
    try:
        option_chain = get_option_chain(symbol, is_index=True)
        print(f"Option Chain for {symbol}: {option_chain}")
    except Exception as e:
        print(f"Failed to fetch option chain: {e}")

    print("\n")

    # Test get_all_indices
    print("=== Testing get_all_indices ===")

    try:
        indices = get_all_indices()
        print("All Indices:", indices)
    except Exception as e:
        print(f"Failed to fetch indices: {e}")
    print("\n")

    # Test get_corporate_actions
    print("=== Testing get_corporate_actions ===")
    try:
        corporate_actions = get_corporate_actions(segment="equities")
        print("Corporate Actions:", corporate_actions)
    except Exception as e:
        print(f"Failed to fetch corporate actions: {e}")

    print("\n")

    # Test get_announcements
    print("=== Testing get_announcements ===")
    try:
        announcements = get_announcements(index="equities")
        print("Corporate Announcements:", announcements)
    except Exception as e:
        print(f"Failed to fetch announcements: {e}")
    print("\n")

    # Test get_holidays (trading)
    print("=== Testing get_holidays (trading) ===")
    try:
        trading_holidays = get_holidays(holiday_type="trading")
        print("Trading Holidays:", trading_holidays)
    except Exception as e:
        print(f"Failed to fetch trading holidays: {e}")
    print("\n")

    # Test get_holidays (clearing)
    print("=== Testing get_holidays (clearing) ===")

    try:
        clearing_holidays = get_holidays(holiday_type="clearing")
        print("Clearing Holidays:", clearing_holidays)

    except Exception as e:
        print(f"Failed to fetch clearing holidays: {e}")
    print("\n")


    # Test bulk_deals
    print("=== Testing bulk_deals ===")
    from_date = datetime(2023, 1, 1)

    to_date = datetime(2023, 12, 31)
    try:
        bulk_deals_data = bulk_deals(from_date, to_date)

        print("Bulk Deals:", bulk_deals_data)
    except Exception as e:

        print(f"Failed to fetch bulk deals: {e}")
    print("\n")

    # Test get_fii_dii_data

    print("=== Testing get_fii_dii_data ===")

    try:
        fii_dii_data = get_fii_dii_data()
        print("FII/DII Data:", fii_dii_data)
    except Exception as e:
        print(f"Failed to fetch FII/DII data: {e}")
    print("\n")


    # Test get_top_gainers
    print("=== Testing get_top_gainers ===")
    try:
        top_gainers = get_top_gainers()
        print("Top Gainers:", top_gainers)
    except Exception as e:
        print(f"Failed to fetch top gainers: {e}")
    print("\n")

    # Test get_top_losers
    print("=== Testing get_top_losers ===")
    try:
        top_losers = get_top_losers()
        print("Top Losers:", top_losers)
    except Exception as e:
        print(f"Failed to fetch top losers: {e}")

    print("\n")

    # Test get_regulatory_status

    print("=== Testing get_regulatory_status ===")
    try:

        regulatory_status = get_regulatory_status()
        print("Regulatory Status:", regulatory_status)
    except Exception as e:
        print(f"Failed to fetch regulatory status: {e}")
    print("\n")

if __name__ == "__main__":
    main()
