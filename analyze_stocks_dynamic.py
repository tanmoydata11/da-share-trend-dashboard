"""
DYNAMIC STOCK ANALYSIS ENGINE
Reads stocks from stocks_config.json
Analyzes data from Stock_Tracker_Fixed.xlsx
Generates dashboard_data.json for HTML pages
"""

import pandas as pd
import json
from datetime import datetime

# Configuration
EXCEL_FILE = 'Stock_Tracker_Fixed.xlsx'
CONFIG_FILE = 'stocks_config.json'
OUTPUT_FILE = '/home/claude/dashboard_data.json'


def load_config():
    """Load stock configuration from JSON"""
    print("📋 Loading stock configuration...")
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        print(f"✓ Loaded {len(config['stocks'])} stocks from config")
        return config
    except FileNotFoundError:
        print(f"❌ Error: {CONFIG_FILE} not found!")
        return None
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None


def load_stock_data():
    """Load data from Excel file"""
    print(f"\n📂 Loading Excel data from {EXCEL_FILE}...")
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"✓ Loaded {len(df)} rows of data")
        return df
    except FileNotFoundError:
        print(f"❌ Error: {EXCEL_FILE} not found!")
        return None
    except Exception as e:
        print(f"❌ Error loading Excel: {e}")
        return None


def get_stock_symbol_mapping(config):
    """Create mapping from symbol to display name"""
    mapping = {}
    for stock in config['stocks']:
        # Remove .NS suffix for display
        symbol = stock['symbol'].replace('.NS', '')
        mapping[symbol] = {
            'display_name': symbol,
            'sector': stock['sector']
        }
    return mapping


def analyze_stock(stock_name, stock_data_with_time):
    """
    Analyze individual stock
    Returns dict with all metrics
    """
    if len(stock_data_with_time) < 2:
        return None
    
    # Basic prices
    open_price = stock_data_with_time[stock_name].iloc[0]
    close_price = stock_data_with_time[stock_name].iloc[-1]
    
    # Find HIGH and its time
    high_idx = stock_data_with_time[stock_name].idxmax()
    high_price = stock_data_with_time.loc[high_idx, stock_name]
    high_time = stock_data_with_time.loc[high_idx, 'Time']
    
    # Find LOW and its time
    low_idx = stock_data_with_time[stock_name].idxmin()
    low_price = stock_data_with_time.loc[low_idx, stock_name]
    low_time = stock_data_with_time.loc[low_idx, 'Time']
    
    # Format times
    if isinstance(high_time, str):
        high_time_str = high_time
    else:
        high_time_str = high_time.strftime('%I:%M %p') if hasattr(high_time, 'strftime') else str(high_time)
    
    if isinstance(low_time, str):
        low_time_str = low_time
    else:
        low_time_str = low_time.strftime('%I:%M %p') if hasattr(low_time, 'strftime') else str(low_time)
    
    # Calculate metrics
    change = close_price - open_price
    change_pct = (change / open_price) * 100
    
    # Shadow prices
    green_shadow = high_price - close_price  # How much dropped from peak
    red_shadow = open_price - low_price      # How much fell from opening
    
    return {
        'name': stock_name,
        'open': round(float(open_price), 2),
        'close': round(float(close_price), 2),
        'high': round(float(high_price), 2),
        'high_time': high_time_str,
        'low': round(float(low_price), 2),
        'low_time': low_time_str,
        'change': round(float(change), 2),
        'change_pct': round(float(change_pct), 2),
        'green_shadow': round(float(green_shadow), 2),
        'red_shadow': round(float(red_shadow), 2)
    }


def analyze_latest_day(df, config):
    """
    Analyze the most recent trading day
    Returns dict with all stocks analyzed
    """
    print("\n📊 Analyzing latest trading day...")
    
    # Get stock columns from config
    stock_symbols = [s['symbol'].replace('.NS', '') for s in config['stocks']]
    
    # Get actual column names from Excel (some might be missing)
    available_stocks = [col for col in df.columns if col in stock_symbols]
    
    # Find latest date WITH actual data
    dates = sorted(df['Date'].unique(), reverse=True)
    latest_date = None
    
    for date in dates:
        date_data = df[df['Date'] == date]
        # Check if any stock has data on this date
        for stock in available_stocks:
            if date_data[stock].dropna().shape[0] > 0:
                latest_date = date
                break
        if latest_date:
            break
    
    if not latest_date:
        print("   ❌ No data found!")
        return None
    
    print(f"   Latest date with data: {latest_date}")
    
    # Filter data for latest date
    latest_data = df[df['Date'] == latest_date]
    
    print(f"   Analyzing {len(available_stocks)} stocks...")
    
    all_stocks = []
    gainers = []
    losers = []
    
    # Analyze each stock
    for stock in available_stocks:
        stock_data_with_time = latest_data[['Time', stock]].dropna()
        
        result = analyze_stock(stock, stock_data_with_time)
        if result:
            all_stocks.append(result)
            
            # Categorize
            if result['change_pct'] > 0:
                gainers.append(result)
            elif result['change_pct'] < 0:
                losers.append(result)
    
    # Sort
    gainers = sorted(gainers, key=lambda x: x['change_pct'], reverse=True)
    losers = sorted(losers, key=lambda x: x['change_pct'])
    
    print(f"   ✓ Found {len(gainers)} gainers, {len(losers)} losers")
    
    return {
        'date': str(latest_date),
        'all_stocks': all_stocks,
        'gainers': gainers,
        'losers': losers
    }


def calculate_portfolio_metrics(all_stocks):
    """Calculate overall portfolio metrics"""
    shares_per_stock = 100
    
    total_value = 0
    total_change = 0
    
    for stock in all_stocks:
        stock_value = stock['close'] * shares_per_stock
        stock_change = stock['change'] * shares_per_stock
        
        total_value += stock_value
        total_change += stock_change
    
    if total_value > 0:
        change_pct = (total_change / (total_value - total_change)) * 100
    else:
        change_pct = 0
    
    return {
        'total': round(total_value, 2),
        'change': round(total_change, 2),
        'change_pct': round(change_pct, 2)
    }


def generate_insights(analysis):
    """Generate trading insights"""
    gainers = analysis['gainers']
    losers = analysis['losers']
    
    insights = []
    
    # Market mood
    gainers_count = len(gainers)
    losers_count = len(losers)
    
    if gainers_count > losers_count:
        mood = "positive"
        mood_emoji = "😊"
        insights.append("Overall market is positive today - Good day to stay invested")
    elif losers_count > gainers_count:
        mood = "negative"
        mood_emoji = "😟"
        insights.append("Market is down today - Be cautious with new investments")
    else:
        mood = "neutral"
        mood_emoji = "😐"
        insights.append("Market is mixed today - Wait for clear signals")
    
    # Top performer
    if gainers:
        top = gainers[0]
        insights.append(
            f"{top['name']} is top performer (+{top['change_pct']}%) - "
            f"Hit ₹{top['high']} at {top['high_time']}"
        )
    
    # Biggest loser
    if losers:
        worst = losers[0]
        insights.append(
            f"Avoid {worst['name']} today ({worst['change_pct']}%) - "
            f"Dropped to ₹{worst['low']} at {worst['low_time']}"
        )
    
    return {
        'mood': mood,
        'mood_emoji': mood_emoji,
        'list': insights
    }


def save_dashboard_data(analysis, config):
    """Save all data to JSON for HTML consumption"""
    print(f"\n💾 Saving dashboard data to {OUTPUT_FILE}...")
    
    portfolio = calculate_portfolio_metrics(analysis['all_stocks'])
    insights = generate_insights(analysis)
    
    # Prepare output
    output = {
        'date': analysis['date'],
        'updated_time': datetime.now().strftime('%I:%M %p'),
        'mood': insights['mood'],
        'mood_emoji': insights['mood_emoji'],
        'portfolio': portfolio,
        'stats': {
            'total_stocks': len(analysis['all_stocks']),
            'gainers_count': len(analysis['gainers']),
            'losers_count': len(analysis['losers']),
            'avg_volatility': round(
                sum(abs(s['change_pct']) for s in analysis['all_stocks']) / len(analysis['all_stocks']),
                2
            ) if analysis['all_stocks'] else 0
        },
        'top_gainers': analysis['gainers'][:3],
        'top_losers': analysis['losers'][:3],
        'all_stocks': analysis['all_stocks'],
        'insights': insights['list']
    }
    
    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Dashboard data saved!")
    return output


def print_summary(data):
    """Print summary to console"""
    print("\n" + "=" * 70)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 70)
    
    print(f"\n📅 Date: {data['date']}")
    print(f"🕐 Updated: {data['updated_time']}")
    print(f"\n{data['mood_emoji']} Market Mood: {data['mood'].upper()}")
    
    print(f"\n💰 Portfolio:")
    print(f"   Value: ₹{data['portfolio']['total']:,.2f}")
    print(f"   Change: ₹{data['portfolio']['change']:,.2f} ({data['portfolio']['change_pct']:+.2f}%)")
    
    print(f"\n📊 Statistics:")
    print(f"   Total Stocks: {data['stats']['total_stocks']}")
    print(f"   Gainers: {data['stats']['gainers_count']}")
    print(f"   Losers: {data['stats']['losers_count']}")
    print(f"   Avg Volatility: {data['stats']['avg_volatility']}%")
    
    print(f"\n🏆 Top 3 Gainers:")
    for stock in data['top_gainers']:
        print(f"   {stock['name']}: ₹{stock['close']} (+{stock['change_pct']}%)")
    
    print(f"\n⚠️  Top 3 Losers:")
    for stock in data['top_losers']:
        print(f"   {stock['name']}: ₹{stock['close']} ({stock['change_pct']}%)")
    
    print("\n" + "=" * 70)


def main():
    """Main execution"""
    print("=" * 70)
    print("🚀 DYNAMIC STOCK ANALYSIS ENGINE")
    print("=" * 70)
    
    # Step 1: Load configuration
    config = load_config()
    if not config:
        return
    
    # Step 2: Load Excel data
    df = load_stock_data()
    if df is None:
        return
    
    # Step 3: Analyze
    analysis = analyze_latest_day(df, config)
    
    # Step 4: Save dashboard data
    data = save_dashboard_data(analysis, config)
    
    # Step 5: Print summary
    print_summary(data)
    
    print("\n✓ Analysis complete!")
    print(f"✓ Data saved to {OUTPUT_FILE}")
    print("\n💡 Next: Open index.html in your browser")


if __name__ == "__main__":
    main()
