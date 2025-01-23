from flask import Flask, jsonify, request
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
    get_most_active_equities,
    get_most_active_sme,
    get_most_active_etf,
    get_volume_gainers,
    get_all_indices_performance,
    get_price_band_hitters,
    get_52_week_high,
    get_52_week_low,
    get_52_week_counts,
    get_52_week_data_by_symbol,
    get_large_deals,
    get_advance_data,
    get_decline_data,
    get_unchanged_data,
    get_stocks_traded,
    get_stocks_traded_by_symbol,
)

app = Flask(__name__)

@app.route('/market-status', methods=['GET'])
def market_status():
    status = get_market_status()
    return jsonify(status)

@app.route('/stock-quote/<symbol>', methods=['GET'])
def stock_quote(symbol):
    quote = get_stock_quote(symbol)
    return jsonify(quote)

@app.route('/option-chain/<symbol>', methods=['GET'])
def option_chain(symbol):
    is_index = request.args.get('is_index', default=False, type=lambda v: v.lower() == 'true')
    chain = get_option_chain(symbol, is_index=is_index)
    return jsonify(chain)

@app.route('/all-indices', methods=['GET'])
def all_indices():
    indices = get_all_indices()
    return jsonify(indices)

@app.route('/corporate-actions', methods=['GET'])
def corporate_actions():
    segment = request.args.get('segment', default='equities')
    symbol = request.args.get('symbol', default=None)
    from_date = request.args.get('from_date', default=None)
    to_date = request.args.get('to_date', default=None)

    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

    actions = get_corporate_actions(segment=segment, symbol=symbol, from_date=from_date, to_date=to_date)
    return jsonify(actions)

@app.route('/announcements', methods=['GET'])
def announcements():
    index = request.args.get('index', default='equities')
    symbol = request.args.get('symbol', default=None)
    fno = request.args.get('fno', default=False, type=lambda v: v.lower() == 'true')
    from_date = request.args.get('from_date', default=None)
    to_date = request.args.get('to_date', default=None)

    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

    announcements = get_announcements(index=index, symbol=symbol, fno=fno, from_date=from_date, to_date=to_date)
    return jsonify(announcements)

@app.route('/holidays', methods=['GET'])
def holidays():
    holiday_type = request.args.get('type', default='trading')
    holidays = get_holidays(holiday_type=holiday_type)
    return jsonify(holidays)

@app.route('/bulk-deals', methods=['GET'])
def bulk_deals_route():
    from_date = request.args.get('from_date', default=None)
    to_date = request.args.get('to_date', default=None)

    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

    deals = bulk_deals(from_date=from_date, to_date=to_date)
    return jsonify(deals)

@app.route('/fii-dii-data', methods=['GET'])
def fii_dii_data():
    data = get_fii_dii_data()
    return jsonify(data)

@app.route('/top-gainers', methods=['GET'])
def top_gainers():
    gainers = get_top_gainers()
    return jsonify(gainers)

@app.route('/top-losers', methods=['GET'])
def top_losers():
    losers = get_top_losers()
    return jsonify(losers)

@app.route('/regulatory-status', methods=['GET'])
def regulatory_status():
    status = get_regulatory_status()
    return jsonify(status)

@app.route('/most-active-equities', methods=['GET'])
def most_active_equities():
    index = request.args.get('index', default='volume')
    equities = get_most_active_equities(index=index)
    return jsonify(equities)

@app.route('/most-active-sme', methods=['GET'])
def most_active_sme():
    index = request.args.get('index', default='volume')
    sme = get_most_active_sme(index=index)
    return jsonify(sme)

@app.route('/most-active-etf', methods=['GET'])
def most_active_etf():
    index = request.args.get('index', default='volume')
    etf = get_most_active_etf(index=index)
    return jsonify(etf)

@app.route('/volume-gainers', methods=['GET'])
def volume_gainers():
    gainers = get_volume_gainers()
    return jsonify(gainers)

@app.route('/all-indices-performance', methods=['GET'])
def all_indices_performance():
    performance = get_all_indices_performance()
    return jsonify(performance)

@app.route('/price-band-hitters', methods=['GET'])
def price_band_hitters():
    band_type = request.args.get('band_type', default='upper')
    category = request.args.get('category', default='AllSec')
    hitters = get_price_band_hitters(band_type=band_type, category=category)
    return jsonify(hitters)

@app.route('/52-week-high', methods=['GET'])
def week_high():
    high = get_52_week_high()
    return jsonify(high)

@app.route('/52-week-low', methods=['GET'])
def week_low():
    low = get_52_week_low()
    return jsonify(low)

@app.route('/52-week-counts', methods=['GET'])
def week_counts():
    counts = get_52_week_counts()
    return jsonify(counts)

@app.route('/52-week-data/<symbol>', methods=['GET'])
def week_data(symbol):
    data = get_52_week_data_by_symbol(symbol)
    return jsonify(data)

@app.route('/large-deals', methods=['GET'])
def large_deals():
    deals = get_large_deals()
    return jsonify(deals)

@app.route('/advance-data', methods=['GET'])
def advance_data():
    symbol = request.args.get('symbol', default=None)
    data = get_advance_data(symbol=symbol)
    return jsonify(data)

@app.route('/decline-data', methods=['GET'])
def decline_data():
    symbol = request.args.get('symbol', default=None)
    data = get_decline_data(symbol=symbol)
    return jsonify(data)

@app.route('/unchanged-data', methods=['GET'])
def unchanged_data():
    symbol = request.args.get('symbol', default=None)
    data = get_unchanged_data(symbol=symbol)
    return jsonify(data)

@app.route('/stocks-traded', methods=['GET'])
def stocks_traded():
    data = get_stocks_traded()
    return jsonify(data)

@app.route('/stocks-traded/<symbol>', methods=['GET'])
def stocks_traded_by_symbol(symbol):
    data = get_stocks_traded_by_symbol(symbol)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
