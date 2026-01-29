"""
ENHANCED STOCK ANALYSIS WITH EMA & TRENDS
Generates detailed analysis for each stock including:
- 9-day, 20-day, 200-day EMAs
- Trend analysis
- Historical price data for charts
"""

import pandas as pd
import json
from datetime import datetime
import os

# Configuration
EXCEL_FILE = 'Stock_Tracker_Fixed.xlsx'
CONFIG_FILE = 'stocks_config.json'
OUTPUT_FILE = 'dashboard_data.json'
STOCK_DETAILS_DIR = 'stock_details'


def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    prices_series = pd.Series(prices)
    ema = prices_series.ewm(span=period, adjust=False).mean()
    return round(float(ema.iloc[-1]), 2)


def analyze_trend(current_price, ema_9, ema_20, ema_200):
    """Analyze trend based on EMAs"""
    trends = []
    
    if ema_9:
        if current_price > ema_9:
            trends.append("bullish_short")
        else:
            trends.append("bearish_short")
    
    if ema_20:
        if current_price > ema_20:
            trends.append("bullish_medium")
        else:
            trends.append("bearish_medium")
    
    if ema_200:
        if current_price > ema_200:
            trends.append("bullish_long")
        else:
            trends.append("bearish_long")
    
    bullish_count = sum(1 for t in trends if 'bullish' in t)
    bearish_count = sum(1 for t in trends if 'bearish' in t)
    
    if bullish_count > bearish_count:
        overall = "Bullish"
        signal = "BUY"
    elif bearish_count > bullish_count:
        overall = "Bearish"
        signal = "SELL"
    else:
        overall = "Neutral"
        signal = "HOLD"
    
    return {
        'overall': overall,
        'signal': signal,
        'short_term': 'Bullish' if 'bullish_short' in trends else 'Bearish',
        'medium_term': 'Bullish' if 'bullish_medium' in trends else 'Bearish',
        'long_term': 'Bullish' if 'bullish_long' in trends else 'Bearish' if ema_200 else 'N/A'
    }


def get_historical_close_prices(df, stock_name):
    """Get daily closing prices"""
    daily_closes = []
    dates = sorted(df['Date'].unique())
    
    for date in dates:
        date_data = df[df['Date'] == date][stock_name].dropna()
        if len(date_data) > 0:
            close_price = date_data.iloc[-1]
            daily_closes.append(float(close_price))
    
    return daily_closes


def get_intraday_data(df, stock_name, date):
    """Get intraday data"""
    date_data = df[df['Date'] == date][['Time', stock_name]].dropna()
    
    intraday = []
    for _, row in date_data.iterrows():
        time_str = str(row['Time'])
        price = float(row[stock_name])
        intraday.append({'time': time_str, 'price': price})
    
    return intraday


def generate_stock_detail_file(df, stock_name, stock_info, latest_date):
    """Generate detailed JSON for individual stock"""
    
    daily_closes = get_historical_close_prices(df, stock_name)
    
    ema_9 = calculate_ema(daily_closes, 9) if len(daily_closes) >= 9 else None
    ema_20 = calculate_ema(daily_closes, 20) if len(daily_closes) >= 20 else None
    ema_200 = calculate_ema(daily_closes, 200) if len(daily_closes) >= 200 else None
    
    trend = analyze_trend(stock_info['close'], ema_9, ema_20, ema_200)
    
    last_10_days = daily_closes[-10:] if len(daily_closes) >= 10 else daily_closes
    dates = sorted(df['Date'].unique())
    last_10_dates = [str(d) for d in dates[-len(last_10_days):]]
    
    intraday_data = get_intraday_data(df, stock_name, latest_date)
    
    recent_highs = []
    recent_lows = []
    for date in dates[-10:]:
        date_data = df[df['Date'] == date][stock_name].dropna()
        if len(date_data) > 0:
            recent_highs.append(float(date_data.max()))
            recent_lows.append(float(date_data.min()))
    
    resistance = round(max(recent_highs), 2) if recent_highs else stock_info['high']
    support = round(min(recent_lows), 2) if recent_lows else stock_info['low']
    
    detail_data = {
        'name': stock_name,
        'current_price': stock_info['close'],
        'open': stock_info['open'],
        'high': stock_info['high'],
        'low': stock_info['low'],
        'change': stock_info['change'],
        'change_pct': stock_info['change_pct'],
        'date': latest_date,
        'updated_time': datetime.now().strftime('%I:%M %p'),
        'ema': {
            'ema_9': ema_9,
            'ema_20': ema_20,
            'ema_200': ema_200
        },
        'trend': trend,
        'support_resistance': {
            'resistance': resistance,
            'support': support,
            'distance_to_resistance': round(resistance - stock_info['close'], 2),
            'distance_to_support': round(stock_info['close'] - support, 2)
        },
        'historical': {
            'dates': last_10_dates,
            'prices': last_10_days
        },
        'intraday': intraday_data,
        'shadows': {
            'green_shadow': stock_info['green_shadow'],
            'red_shadow': stock_info['red_shadow']
        },
        'key_levels': {
            'day_high': stock_info['high'],
            'day_high_time': stock_info['high_time'],
            'day_low': stock_info['low'],
            'day_low_time': stock_info['low_time']
        }
    }
    
    return detail_data


def load_config():
    """Load stock configuration"""
    print("📋 Loading stock configuration...")
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"✓ Loaded {len(config['stocks'])} stocks from config")
        return config
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def load_stock_data():
    """Load Excel data"""
    print(f"\n📂 Loading Excel data from {EXCEL_FILE}...")
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"✓ Loaded {len(df)} rows")
        return df
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def analyze_stock(stock_name, stock_data_with_time):
    """Analyze individual stock"""
    if len(stock_data_with_time) < 2:
        return None
    
    open_price = stock_data_with_time[stock_name].iloc[0]
    close_price = stock_data_with_time[stock_name].iloc[-1]
    
    high_idx = stock_data_with_time[stock_name].idxmax()
    high_price = stock_data_with_time.loc[high_idx, stock_name]
    high_time = str(stock_data_with_time.loc[high_idx, 'Time'])
    
    low_idx = stock_data_with_time[stock_name].idxmin()
    low_price = stock_data_with_time.loc[low_idx, stock_name]
    low_time = str(stock_data_with_time.loc[low_idx, 'Time'])
    
    change = close_price - open_price
    change_pct = (change / open_price) * 100
    
    return {
        'name': stock_name,
        'open': round(float(open_price), 2),
        'close': round(float(close_price), 2),
        'high': round(float(high_price), 2),
        'high_time': high_time,
        'low': round(float(low_price), 2),
        'low_time': low_time,
        'change': round(float(change), 2),
        'change_pct': round(float(change_pct), 2),
        'green_shadow': round(float(high_price - close_price), 2),
        'red_shadow': round(float(open_price - low_price), 2)
    }


def analyze_latest_day(df, config):
    """Analyze latest day"""
    print("\n📊 Analyzing latest trading day...")
    
    stock_symbols = [s['symbol'].replace('.NS', '') for s in config['stocks']]
    available_stocks = [col for col in df.columns if col in stock_symbols]
    
    dates = sorted(df['Date'].unique(), reverse=True)
    latest_date = None
    
    for date in dates:
        date_data = df[df['Date'] == date]
        for stock in available_stocks:
            if date_data[stock].dropna().shape[0] > 0:
                latest_date = date
                break
        if latest_date:
            break
    
    if not latest_date:
        return None
    
    print(f"   Latest date: {latest_date}")
    
    latest_data = df[df['Date'] == latest_date]
    all_stocks = []
    gainers = []
    losers = []
    
    for stock in available_stocks:
        stock_data_with_time = latest_data[['Time', stock]].dropna()
        result = analyze_stock(stock, stock_data_with_time)
        if result:
            all_stocks.append(result)
            if result['change_pct'] > 0:
                gainers.append(result)
            elif result['change_pct'] < 0:
                losers.append(result)
    
    gainers = sorted(gainers, key=lambda x: x['change_pct'], reverse=True)
    losers = sorted(losers, key=lambda x: x['change_pct'])
    
    print(f"   ✓ {len(gainers)} gainers, {len(losers)} losers")
    
    return {
        'date': str(latest_date),
        'all_stocks': all_stocks,
        'gainers': gainers,
        'losers': losers
    }


def save_dashboard_data(analysis):
    """Save dashboard data"""
    print(f"\n💾 Saving {OUTPUT_FILE}...")
    
    gainers_count = len(analysis['gainers'])
    losers_count = len(analysis['losers'])
    
    if gainers_count > losers_count:
        mood, mood_emoji = "positive", "😊"
    elif losers_count > gainers_count:
        mood, mood_emoji = "negative", "😟"
    else:
        mood, mood_emoji = "neutral", "😐"
    
    shares = 100
    total_value = sum(s['close'] * shares for s in analysis['all_stocks'])
    total_change = sum(s['change'] * shares for s in analysis['all_stocks'])
    change_pct = (total_change / (total_value - total_change)) * 100 if total_value > 0 else 0
    
    output = {
        'date': analysis['date'],
        'updated_time': datetime.now().strftime('%I:%M %p'),
        'mood': mood,
        'mood_emoji': mood_emoji,
        'portfolio': {
            'total': round(total_value, 2),
            'change': round(total_change, 2),
            'change_pct': round(change_pct, 2)
        },
        'stats': {
            'total_stocks': len(analysis['all_stocks']),
            'gainers_count': gainers_count,
            'losers_count': losers_count,
            'avg_volatility': round(sum(abs(s['change_pct']) for s in analysis['all_stocks']) / len(analysis['all_stocks']), 2) if analysis['all_stocks'] else 0
        },
        'top_gainers': analysis['gainers'][:3],
        'top_losers': analysis['losers'][:3],
        'all_stocks': analysis['all_stocks'],
        'insights': []
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("✓ Saved")
    return output


def save_individual_stock_details(df, analysis):
    """Save detailed data for each stock"""
    print(f"\n📊 Generating stock details...")
    
    if not os.path.exists(STOCK_DETAILS_DIR):
        os.makedirs(STOCK_DETAILS_DIR)
    
    for stock_info in analysis['all_stocks']:
        stock_name = stock_info['name']
        detail_data = generate_stock_detail_file(df, stock_name, stock_info, analysis['date'])
        
        filename = f"{STOCK_DETAILS_DIR}/{stock_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detail_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ {stock_name}.json")
    
    print(f"✓ Saved to {STOCK_DETAILS_DIR}/")


def main():
    """Main execution"""
    print("=" * 70)
    print("🚀 ENHANCED STOCK ANALYSIS WITH EMA")
    print("=" * 70)
    
    config = load_config()
    if not config:
        return
    
    df = load_stock_data()
    if df is None:
        return
    
    analysis = analyze_latest_day(df, config)
    if not analysis:
        return
    
    save_dashboard_data(analysis)
    save_individual_stock_details(df, analysis)
    
    print("\n✓ Complete!")
    print(f"✓ Dashboard: {OUTPUT_FILE}")
    print(f"✓ Details: {STOCK_DETAILS_DIR}/")


if __name__ == "__main__":
    main()
