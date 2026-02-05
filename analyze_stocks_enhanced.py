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
import shutil

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


def clear_old_data():
    """Clear old data files before generating new analysis"""
    print("🗑️  Clearing old data...")
    
    # Remove old dashboard file
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
        print(f"   ✓ Removed {OUTPUT_FILE}")
    
    # Remove old stock details directory
    if os.path.exists(STOCK_DETAILS_DIR):
        shutil.rmtree(STOCK_DETAILS_DIR)
        print(f"   ✓ Removed {STOCK_DETAILS_DIR}/")
    
    print()


def load_stock_data():
    """Load Excel data"""
    print(f"\n📂 Loading Excel data from {EXCEL_FILE}...")
    try:
        df = pd.read_excel(EXCEL_FILE)
        
        # Remove rows where all stock columns are NaN
        stock_symbols = [col for col in df.columns if col not in ['Date', 'Time', 'Day', 'Sector']]
        df = df.dropna(subset=stock_symbols, how='all')
        
        print(f"✓ Loaded {len(df)} rows")
        print(f"✓ Date range: {df['Date'].min()} to {df['Date'].max()}")
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


def analyze_date_range(df, config):
    """Analyze entire date range (01-01-2026 to 31-12-2026)"""
    print("\n📊 Analyzing full date range...")
    
    stock_symbols = [s['symbol'].replace('.NS', '') for s in config['stocks']]
    available_stocks = [col for col in df.columns if col in stock_symbols]
    
    dates = sorted(df['Date'].unique())
    print(f"   Date range: {dates[0]} to {dates[-1]}")
    print(f"   Total trading days: {len(dates)}")
    
    all_stocks_yearly = {}
    
    # Initialize stock tracking
    for stock in available_stocks:
        all_stocks_yearly[stock] = {
            'prices': [],
            'dates': [],
            'daily_opens': [],
            'daily_closes': [],
            'daily_highs': [],
            'daily_lows': []
        }
    
    # Process each date
    for date in dates:
        date_data = df[df['Date'] == date]
        
        for stock in available_stocks:
            stock_data_with_time = date_data[['Time', stock]].dropna()
            
            if len(stock_data_with_time) > 0:
                prices = stock_data_with_time[stock].values
                all_stocks_yearly[stock]['prices'].extend(prices)
                all_stocks_yearly[stock]['dates'].append(str(date))
                all_stocks_yearly[stock]['daily_opens'].append(float(prices[0]))
                all_stocks_yearly[stock]['daily_closes'].append(float(prices[-1]))
                all_stocks_yearly[stock]['daily_highs'].append(float(max(prices)))
                all_stocks_yearly[stock]['daily_lows'].append(float(min(prices)))
    
    # Calculate yearly statistics
    stock_analysis = []
    
    for stock in available_stocks:
        stock_data = all_stocks_yearly[stock]
        
        if len(stock_data['prices']) == 0:
            continue
        
        yearly_open = stock_data['daily_opens'][0]
        yearly_close = stock_data['daily_closes'][-1]
        yearly_high = max(stock_data['daily_highs'])
        yearly_low = min(stock_data['daily_lows'])
        yearly_change = yearly_close - yearly_open
        yearly_change_pct = (yearly_change / yearly_open) * 100
        
        avg_price = sum(stock_data['prices']) / len(stock_data['prices'])
        
        stock_analysis.append({
            'name': stock,
            'yearly_open': round(yearly_open, 2),
            'yearly_close': round(yearly_close, 2),
            'yearly_high': round(yearly_high, 2),
            'yearly_low': round(yearly_low, 2),
            'yearly_change': round(yearly_change, 2),
            'yearly_change_pct': round(yearly_change_pct, 2),
            'avg_price': round(avg_price, 2),
            'trading_days': len(stock_data['daily_closes']),
            'prices_data': stock_data
        })
    
    gainers = sorted([s for s in stock_analysis if s['yearly_change_pct'] > 0], 
                     key=lambda x: x['yearly_change_pct'], reverse=True)
    losers = sorted([s for s in stock_analysis if s['yearly_change_pct'] < 0], 
                    key=lambda x: x['yearly_change_pct'])
    
    print(f"   ✓ {len(gainers)} gainers, {len(losers)} losers")
    
    return {
        'date_range': f"{dates[0]} to {dates[-1]}",
        'total_trading_days': len(dates),
        'all_stocks': stock_analysis,
        'gainers': gainers,
        'losers': losers,
        'analysis_type': 'yearly'
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


def analyze_sectors(config, formatted_stocks):
    """Analyze performance by sector"""
    sector_data = {}
    
    for stock_config in config['stocks']:
        sector = stock_config.get('sector', 'Unknown')
        stock_name = stock_config['symbol']
        
        # Find the stock in formatted stocks
        stock = next((s for s in formatted_stocks if s['name'] == stock_name), None)
        if not stock:
            continue
        
        if sector not in sector_data:
            sector_data[sector] = {
                'name': sector,
                'stocks': [],
                'total_change': 0,
                'avg_change': 0,
                'best_stock': None,
                'worst_stock': None
            }
        
        sector_data[sector]['stocks'].append(stock)
        sector_data[sector]['total_change'] += stock['change_pct']
    
    # Calculate averages and find best/worst
    sectors = []
    for sector_name, data in sector_data.items():
        num_stocks = len(data['stocks'])
        data['avg_change'] = round(data['total_change'] / num_stocks, 2) if num_stocks > 0 else 0
        
        # Find best and worst performers in sector
        sorted_stocks = sorted(data['stocks'], key=lambda x: x['change_pct'], reverse=True)
        data['best_stock'] = {
            'name': sorted_stocks[0]['name'],
            'change_pct': sorted_stocks[0]['change_pct']
        } if sorted_stocks else None
        data['worst_stock'] = {
            'name': sorted_stocks[-1]['name'],
            'change_pct': sorted_stocks[-1]['change_pct']
        } if sorted_stocks else None
        
        sectors.append({
            'name': sector_name,
            'stocks_count': num_stocks,
            'avg_change': data['avg_change'],
            'best_stock': data['best_stock'],
            'worst_stock': data['worst_stock']
        })
    
    # Sort by average change
    sectors.sort(key=lambda x: x['avg_change'], reverse=True)
    
    return sectors


def analyze_sector_time_series(df, config):
    """Analyze sector performance over time (7 days and 1 month)"""
    print("\n📈 Analyzing sector performance over time...")
    
    # Get all dates
    all_dates = sorted(df['Date'].unique())
    
    if len(all_dates) < 7:
        print("⚠️  Not enough data for time series analysis")
        return None
    
    # Get last 7 days and last 30 days
    last_7_dates = all_dates[-7:]
    last_30_dates = all_dates[-30:] if len(all_dates) >= 30 else all_dates
    
    # Group stocks by sector
    sector_stocks = {}
    for stock_config in config['stocks']:
        sector = stock_config.get('sector', 'Unknown')
        stock_name = stock_config['symbol']
        
        if sector not in sector_stocks:
            sector_stocks[sector] = []
        sector_stocks[sector].append(stock_name)
    
    # Calculate 7-day performance
    seven_day_performance = {}
    for sector, stocks in sector_stocks.items():
        daily_changes = []
        
        for i in range(len(last_7_dates)):
            date = last_7_dates[i]
            date_data = df[df['Date'] == date]
            
            sector_avg_change = 0
            valid_stocks = 0
            
            for stock_name in stocks:
                if stock_name in date_data.columns:
                    stock_prices = date_data[stock_name].dropna()
                    if len(stock_prices) >= 2:
                        open_price = stock_prices.iloc[0]
                        close_price = stock_prices.iloc[-1]
                        if open_price > 0:
                            change_pct = ((close_price - open_price) / open_price) * 100
                            sector_avg_change += change_pct
                            valid_stocks += 1
            
            avg_change = round(sector_avg_change / valid_stocks, 2) if valid_stocks > 0 else 0
            daily_changes.append(avg_change)
        
        seven_day_performance[sector] = {
            'dates': [str(d) for d in last_7_dates],
            'daily_changes': daily_changes,
            'total_change': round(sum(daily_changes), 2),
            'avg_change': round(sum(daily_changes) / len(daily_changes), 2) if daily_changes else 0
        }
    
    # Calculate 1-month performance with best/worst stocks
    one_month_performance = {}
    for sector, stocks in sector_stocks.items():
        sector_stock_performance = []
        
        for stock_name in stocks:
            if stock_name in df.columns:
                # Get first and last price in the month
                month_data = df[df['Date'].isin(last_30_dates)][stock_name].dropna()
                
                if len(month_data) >= 2:
                    first_price = month_data.iloc[0]
                    last_price = month_data.iloc[-1]
                    
                    if first_price > 0:
                        change = last_price - first_price
                        change_pct = (change / first_price) * 100
                        
                        sector_stock_performance.append({
                            'name': stock_name,
                            'change': round(change, 2),
                            'change_pct': round(change_pct, 2),
                            'first_price': round(first_price, 2),
                            'last_price': round(last_price, 2)
                        })
        
        # Sort to find best and worst
        if sector_stock_performance:
            sorted_perf = sorted(sector_stock_performance, key=lambda x: x['change_pct'], reverse=True)
            
            one_month_performance[sector] = {
                'stocks_count': len(sector_stock_performance),
                'best_gainer': sorted_perf[0],
                'worst_loser': sorted_perf[-1],
                'avg_change': round(sum(s['change_pct'] for s in sector_stock_performance) / len(sector_stock_performance), 2)
            }
    
    return {
        'seven_day': seven_day_performance,
        'one_month': one_month_performance
    }


def save_yearly_dashboard_data(analysis, config):
    """Save yearly dashboard data"""
    print(f"\n💾 Saving {OUTPUT_FILE}...")
    
    gainers_count = len(analysis['gainers'])
    losers_count = len(analysis['losers'])
    
    if gainers_count > losers_count:
        mood, mood_emoji = "positive", "📈"
    elif losers_count > gainers_count:
        mood, mood_emoji = "negative", "📉"
    else:
        mood, mood_emoji = "neutral", "➡️"
    
    total_change_pct = sum(s['yearly_change_pct'] for s in analysis['all_stocks']) / len(analysis['all_stocks']) if analysis['all_stocks'] else 0
    
    # Calculate portfolio totals
    total_value = sum(s['yearly_close'] * 100 for s in analysis['all_stocks'])
    total_open_value = sum(s['yearly_open'] * 100 for s in analysis['all_stocks'])
    total_change = total_value - total_open_value
    portfolio_change_pct = (total_change / total_open_value * 100) if total_open_value > 0 else 0
    
    # Format stocks for webpage (convert yearly to daily-like format)
    formatted_stocks = []
    for stock in analysis['all_stocks']:
        formatted_stocks.append({
            'name': stock['name'],
            'open': stock['yearly_open'],
            'close': stock['yearly_close'],
            'high': stock['yearly_high'],
            'high_time': '15:30',  # Yearly high time
            'low': stock['yearly_low'],
            'low_time': '09:15',   # Yearly low time
            'change': stock['yearly_change'],
            'change_pct': stock['yearly_change_pct'],
            'green_shadow': round(stock['yearly_high'] - stock['yearly_close'], 2),
            'red_shadow': round(stock['yearly_open'] - stock['yearly_low'], 2)
        })
    
    # Sort for top gainers/losers
    gainers = sorted([s for s in formatted_stocks if s['change_pct'] > 0], 
                     key=lambda x: x['change_pct'], reverse=True)
    losers = sorted([s for s in formatted_stocks if s['change_pct'] < 0], 
                    key=lambda x: x['change_pct'])
    
    # Analyze sectors
    sectors = analyze_sectors(config, formatted_stocks)
    
    # Analyze sector time series (this will be saved separately)
    # We'll save this data later in the main function
    
    output = {
        'date': analysis['date_range'],  # Changed from date_range to date
        'date_range': analysis['date_range'],
        'total_trading_days': analysis['total_trading_days'],
        'generated_time': datetime.now().strftime('%d-%m-%Y %I:%M %p'),
        'updated_time': datetime.now().strftime('%I:%M %p'),
        'mood': mood,
        'mood_emoji': mood_emoji,
        'market_mood': mood,
        'overall_change': round(total_change_pct, 2),
        'portfolio_summary': {
            'total_stocks': len(formatted_stocks),
            'gainers_count': gainers_count,
            'losers_count': losers_count,
            'avg_change_pct': round(total_change_pct, 2)
        },
        'portfolio': {
            'total': round(total_value, 2),
            'change': round(total_change, 2),
            'change_pct': round(portfolio_change_pct, 2)
        },
        'stats': {
            'total_stocks': len(formatted_stocks),
            'gainers_count': gainers_count,
            'losers_count': losers_count,
            'avg_volatility': round(sum(abs(s['change_pct']) for s in formatted_stocks) / len(formatted_stocks), 2) if formatted_stocks else 0
        },
        'market_status': 'Positive' if gainers_count > losers_count else 'Negative' if losers_count > gainers_count else 'Neutral',
        'top_gainers': gainers[:5],
        'top_losers': losers[:5],
        'all_stocks': formatted_stocks,
        'sectors': sectors,
        'insights': [
            f"📊 Analyzed {len(formatted_stocks)} stocks over {analysis['total_trading_days']} trading days",
            f"📈 Top gainer: {gainers[0]['name']} ({gainers[0]['change_pct']}%)" if gainers_count > 0 else "No gainers",
            f"📉 Top loser: {losers[0]['name']} ({losers[0]['change_pct']}%)" if losers_count > 0 else "No losers",
            f"💰 Portfolio value: ₹{total_value:,.2f} | Change: {portfolio_change_pct:+.2f}%"
        ]
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


def save_yearly_stock_details(analysis):
    """Save detailed yearly data for each stock"""
    print(f"\n📊 Generating yearly stock details...")
    
    if not os.path.exists(STOCK_DETAILS_DIR):
        os.makedirs(STOCK_DETAILS_DIR)
    
    for stock_info in analysis['all_stocks']:
        stock_name = stock_info['name']
        prices_data = stock_info['prices_data']
        
        # Calculate EMAs on full year data
        ema_9 = calculate_ema(prices_data['prices'], 9) if len(prices_data['prices']) >= 9 else None
        ema_20 = calculate_ema(prices_data['prices'], 20) if len(prices_data['prices']) >= 20 else None
        ema_200 = calculate_ema(prices_data['prices'], 200) if len(prices_data['prices']) >= 200 else None
        
        # Analyze trends
        trend = analyze_trend(stock_info['yearly_close'], ema_9, ema_20, ema_200)
        
        # Get last 10 days data
        last_10_closes = prices_data['daily_closes'][-10:] if len(prices_data['daily_closes']) >= 10 else prices_data['daily_closes']
        last_10_dates = prices_data['dates'][-len(last_10_closes):]
        
        # Support & Resistance from last 10 days
        last_10_highs = prices_data['daily_highs'][-10:] if len(prices_data['daily_highs']) >= 10 else prices_data['daily_highs']
        last_10_lows = prices_data['daily_lows'][-10:] if len(prices_data['daily_lows']) >= 10 else prices_data['daily_lows']
        
        resistance = round(max(last_10_highs), 2) if last_10_highs else stock_info['yearly_high']
        support = round(min(last_10_lows), 2) if last_10_lows else stock_info['yearly_low']
        
        detail_data = {
            'name': stock_name,
            'current_price': stock_info['yearly_close'],
            'open': stock_info['yearly_open'],
            'high': stock_info['yearly_high'],
            'low': stock_info['yearly_low'],
            'change': stock_info['yearly_change'],
            'change_pct': stock_info['yearly_change_pct'],
            'date': str(analysis['date_range']),
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
                'distance_to_resistance': round(resistance - stock_info['yearly_close'], 2),
                'distance_to_support': round(stock_info['yearly_close'] - support, 2)
            },
            'historical': {
                'dates': last_10_dates,
                'prices': last_10_closes
            },
            'intraday': [
                {'time': '09:15', 'price': prices_data['daily_opens'][0]},
                {'time': '15:30', 'price': prices_data['daily_closes'][-1]}
            ],
            'shadows': {
                'green_shadow': round(stock_info['yearly_high'] - stock_info['yearly_close'], 2),
                'red_shadow': round(stock_info['yearly_open'] - stock_info['yearly_low'], 2)
            },
            'key_levels': {
                'day_high': stock_info['yearly_high'],
                'day_high_time': '15:30',
                'day_low': stock_info['yearly_low'],
                'day_low_time': '09:15'
            }
        }
        
        filename = f"{STOCK_DETAILS_DIR}/{stock_name}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detail_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ {stock_name}.json")
    
    print(f"✓ Saved {len(analysis['all_stocks'])} stock details to {STOCK_DETAILS_DIR}/")


def save_sector_details(df, config):
    """Save detailed sector analysis data"""
    print(f"\n📊 Generating sector details data...")
    
    sector_time_data = analyze_sector_time_series(df, config)
    
    if sector_time_data:
        output_file = 'sector_details_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sector_time_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved sector details to {output_file}")
    else:
        print("⚠️  Could not generate sector details")


def main():
    """Main execution"""
    print("=" * 70)
    print("🚀 ENHANCED STOCK ANALYSIS - FULL YEAR (01-01-2026 to 31-12-2026)")
    print("=" * 70)
    print()
    
    # STEP 1: Clear old data
    clear_old_data()
    
    # STEP 2: Load configuration
    config = load_config()
    if not config:
        return
    
    # STEP 3: Load Excel data
    df = load_stock_data()
    if df is None:
        print("❌ No data in Excel file!")
        return
    
    # STEP 4: Analyze data
    analysis = analyze_date_range(df, config)
    if not analysis:
        print("❌ Analysis failed!")
        return
    
    # STEP 5: Save new data
    save_yearly_dashboard_data(analysis, config)
    save_yearly_stock_details(analysis)
    save_sector_details(df, config)
    
    print("\n" + "=" * 70)
    print("✓ YEARLY ANALYSIS COMPLETE!")
    print("=" * 70)
    print(f"✓ Dashboard: {OUTPUT_FILE}")
    print(f"✓ Details: {STOCK_DETAILS_DIR}/")
    print()
    print("📊 Analysis Summary:")
    print(f"   Total Stocks: {len(analysis['all_stocks'])}")
    print(f"   Trading Days: {analysis['total_trading_days']}")
    print(f"   Gainers: {len(analysis['gainers'])}")
    print(f"   Losers: {len(analysis['losers'])}")
    print(f"   Date Range: {analysis['date_range']}")


if __name__ == "__main__":
    main()
