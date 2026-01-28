"""
SIMPLE STOCK MANAGER - For Your Friends!
They can add/remove stocks WITHOUT touching the main code.
No programming knowledge needed!
"""
import json
import os

STOCKS_CONFIG_FILE = 'stocks_config.json'


def load_config():
    """Load current stocks"""
    if os.path.exists(STOCKS_CONFIG_FILE):
        with open(STOCKS_CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"stocks": []}


def save_config(config):
    """Save stocks configuration"""
    with open(STOCKS_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    print("✓ Configuration saved!")


def show_stocks(config):
    """Display all stocks"""
    print("\n" + "=" * 60)
    print("CURRENT STOCKS")
    print("=" * 60)
    
    if not config['stocks']:
        print("No stocks added yet.")
    else:
        print(f"\nTotal: {len(config['stocks'])} stocks\n")
        print(f"{'#':<4} {'Symbol':<20} {'Sector':<25}")
        print("-" * 60)
        for idx, stock in enumerate(config['stocks'], 1):
            print(f"{idx:<4} {stock['symbol']:<20} {stock['sector']:<25}")
    
    print("=" * 60)


def add_stock(config):
    """Add a new stock"""
    print("\n" + "=" * 60)
    print("ADD NEW STOCK")
    print("=" * 60)
    
    # Get symbol
    symbol = input("\nEnter stock symbol (e.g., RELIANCE.NS): ").strip().upper()
    
    if not symbol:
        print("❌ Symbol cannot be empty!")
        return
    
    # Check if already exists
    for stock in config['stocks']:
        if stock['symbol'] == symbol:
            print(f"❌ {symbol} already exists!")
            return
    
    # Get sector
    print("\nCommon sectors:")
    print("  - IT, Banking, Energy, FMCG, Pharma")
    print("  - Automobile, Metals, Infrastructure, Telecom")
    print("  - Financial Services, Consumer Goods, Electronics")
    
    sector = input("\nEnter sector: ").strip()
    
    if not sector:
        print("❌ Sector cannot be empty!")
        return
    
    # Add stock
    config['stocks'].append({
        "symbol": symbol,
        "sector": sector
    })
    
    save_config(config)
    print(f"\n✓ Added: {symbol} ({sector})")


def remove_stock(config):
    """Remove a stock"""
    show_stocks(config)
    
    if not config['stocks']:
        return
    
    print("\n" + "=" * 60)
    print("REMOVE STOCK")
    print("=" * 60)
    
    try:
        choice = input("\nEnter stock number to remove (or 0 to cancel): ").strip()
        num = int(choice)
        
        if num == 0:
            print("Cancelled.")
            return
        
        if 1 <= num <= len(config['stocks']):
            removed = config['stocks'].pop(num - 1)
            save_config(config)
            print(f"\n✓ Removed: {removed['symbol']} ({removed['sector']})")
        else:
            print("❌ Invalid number!")
    
    except ValueError:
        print("❌ Please enter a number!")


def bulk_add(config):
    """Add multiple stocks at once"""
    print("\n" + "=" * 60)
    print("BULK ADD STOCKS")
    print("=" * 60)
    print("\nEnter stocks in format: SYMBOL.NS,Sector")
    print("One stock per line. Enter blank line when done.")
    print("\nExample:")
    print("  WIPRO.NS,IT")
    print("  TATAMOTORS.NS,Automobile")
    print("  SUNPHARMA.NS,Pharma")
    print()
    
    added = 0
    while True:
        line = input("Stock: ").strip()
        
        if not line:
            break
        
        try:
            symbol, sector = line.split(',')
            symbol = symbol.strip().upper()
            sector = sector.strip()
            
            # Check if exists
            exists = any(s['symbol'] == symbol for s in config['stocks'])
            if exists:
                print(f"  ⚠ {symbol} already exists, skipped")
                continue
            
            config['stocks'].append({
                "symbol": symbol,
                "sector": sector
            })
            added += 1
            print(f"  ✓ Added: {symbol} ({sector})")
        
        except ValueError:
            print(f"  ❌ Invalid format: {line}")
    
    if added > 0:
        save_config(config)
        print(f"\n✓ Added {added} stocks!")


def export_list(config):
    """Export stock list as text"""
    if not config['stocks']:
        print("\nNo stocks to export.")
        return
    
    filename = "stocks_list.txt"
    
    with open(filename, 'w') as f:
        f.write("STOCK LIST\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total: {len(config['stocks'])} stocks\n\n")
        f.write(f"{'Symbol':<20} {'Sector':<25}\n")
        f.write("-" * 60 + "\n")
        
        for stock in config['stocks']:
            f.write(f"{stock['symbol']:<20} {stock['sector']:<25}\n")
    
    print(f"\n✓ Exported to {filename}")


def main():
    """Main menu"""
    while True:
        config = load_config()
        
        print("\n" + "=" * 60)
        print("STOCK MANAGER - Simple & Safe!")
        print("=" * 60)
        print(f"\nCurrent stocks: {len(config['stocks'])}")
        print("\nOptions:")
        print("  1. View all stocks")
        print("  2. Add stock")
        print("  3. Remove stock")
        print("  4. Bulk add (multiple stocks)")
        print("  5. Export list")
        print("  0. Exit")
        print("=" * 60)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            show_stocks(config)
        elif choice == '2':
            add_stock(config)
        elif choice == '3':
            remove_stock(config)
        elif choice == '4':
            bulk_add(config)
        elif choice == '5':
            export_list(config)
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("\n❌ Invalid choice!")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
