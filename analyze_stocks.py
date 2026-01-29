"""
ENHANCED STOCK ANALYSIS ENGINE
Now includes High/Low prices with times for each stock

This script:
1. Reads Stock_Tracker_Fixed.xlsx
2. Calculates performance metrics
3. Finds HIGH and LOW prices with times
4. Generates insights
5. Updates dashboard with real data
"""

import pandas as pd
from datetime import datetime
import json

# Configuration
EXCEL_FILE = 'Stock_Tracker_Fixed.xlsx'
OUTPUT_FILE = 'dashboard_data.json'


def load_stock_data():
    """
    Load data from Excel file
    Returns: pandas DataFrame
    """
    print("📂 Loading Excel data...")
    
    try:
        df = pd.read_excel(EXCEL_FILE)
        print(f"✓ Loaded {len(df)} rows of data")
        print(f"✓ Columns: {', '.join(df.columns[:10])}...")
        return df
    
    except FileNotFoundError:
        print(f"❌ Error: {EXCEL_FILE} not found!")
        print("   Please make sure the Excel file is in the same folder.")
        return None
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def analyze_latest_day(df):
    """
    Analyze the most recent trading day
    NOW INCLUDES: High/Low prices with times
    Returns: dict with analysis results
    """
    print("\n📊 Analyzing latest trading day with High/Low...")
    
    # Get unique dates
    dates = df['Date'].unique()
    latest_date = sorted(dates)[-1]
    
    print(f"   Latest date: {latest_date}")
    
    # Filter data for latest date
    latest_data = df[df['Date'] == latest_date]
    
    # Get stock columns (skip Date, Time, Day, Sector)
    stock_columns = [col for col in df.columns if col not in ['Date', 'Time', 'Day', 'Sector']]
    
    analysis = {
        'date': str(latest_date),
        'total_stocks': len(stock_columns),
        'gainers': [],
        'losers': [],
        'insights': []
    }
    
    # Analyze each stock
    for stock in stock_columns:
        # Get stock data WITH TIME column
        stock_data_with_time = latest_data[['Time', stock]].dropna()
        
        if len(stock_data_with_time) < 2:
            continue
        
        # Basic prices
        open_price = stock_data_with_time[stock].iloc[0]
        close_price = stock_data_with_time[stock].iloc[-1]
        
        # NEW: Find HIGH and its time
        high_idx = stock_data_with_time[stock].idxmax()
        high_price = stock_data_with_time.loc[high_idx, stock]
        high_time = stock_data_with_time.loc[high_idx, 'Time']
        
        # NEW: Find LOW and its time
        low_idx = stock_data_with_time[stock].idxmin()
        low_price = stock_data_with_time.loc[low_idx, stock]
        low_time = stock_data_with_time.loc[low_idx, 'Time']
        
        # Format times (convert to string if needed)
        if isinstance(high_time, str):
            high_time_str = high_time
        else:
            high_time_str = high_time.strftime('%I:%M %p') if hasattr(high_time, 'strftime') else str(high_time)
        
        if isinstance(low_time, str):
            low_time_str = low_time
        else:
            low_time_str = low_time.strftime('%I:%M %p') if hasattr(low_time, 'strftime') else str(low_time)
        
        # Calculate change
        change = close_price - open_price
        change_pct = (change / open_price) * 100
        
        stock_info = {
            'name': stock,
            'open': round(float(open_price), 2),
            'close': round(float(close_price), 2),
            'change': round(float(change), 2),
            'change_pct': round(float(change_pct), 2),
            # NEW: High/Low data
            'high': round(float(high_price), 2),
            'high_time': high_time_str,
            'low': round(float(low_price), 2),
            'low_time': low_time_str
        }
        
        # Categorize as gainer or loser
        if change_pct > 0:
            analysis['gainers'].append(stock_info)
        elif change_pct < 0:
            analysis['losers'].append(stock_info)
    
    # Sort gainers and losers
    analysis['gainers'] = sorted(analysis['gainers'], key=lambda x: x['change_pct'], reverse=True)[:5]
    analysis['losers'] = sorted(analysis['losers'], key=lambda x: x['change_pct'])[:5]
    
    print(f"   ✓ Found {len(analysis['gainers'])} gainers, {len(analysis['losers'])} losers")
    
    return analysis


def calculate_portfolio_value(analysis):
    """
    Calculate total portfolio metrics
    """
    shares_per_stock = 100
    
    total_value = 0
    total_change = 0
    
    for stock in analysis['gainers'] + analysis['losers']:
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
    """
    Generate simple insights for your father
    """
    insights = []
    
    # Overall market mood
    gainers_count = len(analysis['gainers'])
    losers_count = len(analysis['losers'])
    
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
    
    # Top performer insight with high/low
    if analysis['gainers']:
        top_gainer = analysis['gainers'][0]
        insights.append(
            f"{top_gainer['name']} is top performer (+{top_gainer['change_pct']}%) - "
            f"Hit ₹{top_gainer['high']} at {top_gainer['high_time']}"
        )
    
    # Biggest loser insight with high/low
    if analysis['losers']:
        top_loser = analysis['losers'][0]
        insights.append(
            f"Avoid {top_loser['name']} today ({top_loser['change_pct']}%) - "
            f"Dropped to ₹{top_loser['low']} at {top_loser['low_time']}"
        )
    
    return {
        'mood': mood,
        'mood_emoji': mood_emoji,
        'list': insights
    }


def save_to_json(analysis):
    """
    Save analysis results to JSON file
    This JSON will be used to update the dashboard
    """
    print(f"\n💾 Saving analysis to {OUTPUT_FILE}...")
    
    # Calculate portfolio
    portfolio = calculate_portfolio_value(analysis)
    
    # Generate insights
    insights = generate_insights(analysis)
    
    # Combine all data
    output = {
        'date': analysis['date'],
        'updated_time': datetime.now().strftime('%I:%M %p'),
        'mood': insights['mood'],
        'mood_emoji': insights['mood_emoji'],
        'portfolio': portfolio,
        'gainers': analysis['gainers'][:3],  # Top 3
        'losers': analysis['losers'][:3],     # Top 3
        'insights': insights['list']
    }
    
    # Save to JSON
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Analysis saved!")
    
    return output


def print_summary(output):
    """
    Print a nice summary to terminal
    NOW INCLUDES: High/Low with times
    """
    print("\n" + "=" * 70)
    print("📊 ANALYSIS SUMMARY WITH HIGH/LOW")
    print("=" * 70)
    
    print(f"\n📅 Date: {output['date']}")
    print(f"🕐 Updated: {output['updated_time']}")
    
    print(f"\n{output['mood_emoji']} Market Mood: {output['mood'].upper()}")
    
    print(f"\n💰 Portfolio:")
    print(f"   Value: ₹{output['portfolio']['total']:,.2f}")
    print(f"   Change: ₹{output['portfolio']['change']:,.2f} ({output['portfolio']['change_pct']:+.2f}%)")
    
    print(f"\n🏆 Top Gainers:")
    for stock in output['gainers']:
        print(f"\n   {stock['name']}: ₹{stock['close']} (+{stock['change_pct']}%)")
        print(f"      📈 High: ₹{stock['high']} at {stock['high_time']}")
        print(f"      📉 Low:  ₹{stock['low']} at {stock['low_time']}")
    
    print(f"\n⚠️  Top Losers:")
    for stock in output['losers']:
        print(f"\n   {stock['name']}: ₹{stock['close']} ({stock['change_pct']}%)")
        print(f"      📈 High: ₹{stock['high']} at {stock['high_time']}")
        print(f"      📉 Low:  ₹{stock['low']} at {stock['low_time']}")
    
    print(f"\n💡 Insights:")
    for insight in output['insights']:
        print(f"   • {insight}")
    
    print("\n" + "=" * 70)


def main():
    """
    Main analysis pipeline
    """
    print("=" * 70)
    print("🚀 ENHANCED STOCK ANALYSIS ENGINE")
    print("=" * 70)
    
    # Step 1: Load data
    df = load_stock_data()
    if df is None:
        return
    
    # Step 2: Analyze with High/Low
    analysis = analyze_latest_day(df)
    
    # Step 3: Save results
    output = save_to_json(analysis)
    
    # Step 4: Print summary
    print_summary(output)
    
    print("\n✓ Analysis complete!")
    print(f"✓ Data saved to {OUTPUT_FILE}")
    print("\n💡 Next: Open dashboard-complete.html in your browser")


if __name__ == "__main__":
    main()
