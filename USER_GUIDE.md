# MODULAR STOCK TRACKER - USER GUIDE 📚

## 🎯 PROBLEM SOLVED!

**Before:** Friends edit Python code → Code breaks → Disaster! ❌

**Now:** Friends edit JSON file → Safe & Simple → No code touched! ✅

---

## 📁 FILES IN THIS SYSTEM

### 1. **stocks_config.json** ← YOUR FRIENDS EDIT THIS!
- Simple text file with stock list
- JSON format (easy to read/edit)
- No programming knowledge needed
- Safe to edit - won't break anything

### 2. **stock_manager.py** ← OPTIONAL HELPER TOOL
- Simple menu interface for your friends
- Add/Remove stocks without touching JSON
- Even easier than editing JSON directly

### 3. **setup_excel.py** ← RUN WHEN STOCKS CHANGE
- Creates Excel file based on stocks_config.json
- Run once at start
- Re-run when you add/remove stocks

### 4. **populate_modular.py** ← YOUR MAIN DATA FETCHER
- Reads stocks from stocks_config.json
- Fetches data (fast parallel)
- Updates Excel
- YOU control this (friends don't touch it)

---

## 🚀 INITIAL SETUP (One-Time)

### Step 1: Add Your Stocks

**Method A - Use the Manager Tool (Easiest):**
```bash
python stock_manager.py
```

Follow the menu:
- Press `2` to add stock
- Enter: `WIPRO.NS` (symbol)
- Enter: `IT` (sector)
- Repeat for all stocks

**Method B - Edit JSON Directly:**
Open `stocks_config.json` and add stocks:
```json
{
  "stocks": [
    {"symbol": "RELIANCE.NS", "sector": "Energy"},
    {"symbol": "TCS.NS", "sector": "IT"},
    {"symbol": "WIPRO.NS", "sector": "IT"}
  ]
}
```

### Step 2: Create Excel Structure
```bash
python setup_excel.py
```

This creates `Stock_Tracker_Fixed.xlsx` with all your stocks.

### Step 3: Fetch Data
```bash
python populate_modular.py
```

This fills the Excel with stock prices!

---

## 👥 SHARING WITH FRIENDS

### What You Share:
1. `stocks_config.json`
2. `stock_manager.py` (optional, but helpful)
3. Instructions (this guide)

### What You DON'T Share:
- ❌ `populate_modular.py` (you keep this)
- ❌ `setup_excel.py` (you keep this)
- ✅ Only YOU run the data fetcher!

### Instructions for Your Friends:

**"Hey team, when you want to add stocks:"**

**Option 1 - Use the Manager Tool (Recommended):**
```bash
python stock_manager.py
```
- Choose option `2` to add stock
- Enter symbol (e.g., `TATAMOTORS.NS`)
- Enter sector (e.g., `Automobile`)
- Done! Tell me to refresh Excel.

**Option 2 - Edit JSON File:**
```
Open stocks_config.json
Add your stock like:
  {"symbol": "NEWSTOCK.NS", "sector": "Sector Name"}
Save and tell me to refresh Excel.
```

---

## 📊 DAILY WORKFLOW

### Your Friends Add Stocks:
```bash
# Friend runs:
python stock_manager.py
# Adds: WIPRO, SUNPHARMA, LT, etc.
# Tells you: "Added 3 new stocks"
```

### You Update the System:
```bash
# Step 1: Recreate Excel with new stocks
python setup_excel.py

# Step 2: Fetch all data
python populate_modular.py
```

Done! Excel now has the new stocks.

---

## 📝 STOCK MANAGER TOOL GUIDE

When friends run `python stock_manager.py`:

```
============================================================
STOCK MANAGER - Simple & Safe!
============================================================

Current stocks: 24

Options:
  1. View all stocks        ← See what's already added
  2. Add stock             ← Add one stock
  3. Remove stock          ← Remove a stock
  4. Bulk add              ← Add many at once
  5. Export list           ← Save list as text file
  0. Exit
============================================================
```

### Option 1: View All Stocks
Shows complete list with sectors:
```
#    Symbol              Sector
--------------------------------------------------
1    RELIANCE.NS         Energy
2    TCS.NS              IT
3    INFY.NS             IT
...
```

### Option 2: Add Stock
Interactive prompt:
```
Enter stock symbol (e.g., RELIANCE.NS): WIPRO.NS
Enter sector: IT
✓ Added: WIPRO.NS (IT)
```

### Option 3: Remove Stock
Shows numbered list, enter number to remove:
```
Enter stock number to remove: 5
✓ Removed: SOMESTOCK.NS (Sector)
```

### Option 4: Bulk Add
Add multiple stocks at once:
```
Enter stocks in format: SYMBOL.NS,Sector
One per line. Blank line to finish.

Stock: WIPRO.NS,IT
  ✓ Added: WIPRO.NS (IT)
Stock: TATAMOTORS.NS,Automobile
  ✓ Added: TATAMOTORS.NS (Automobile)
Stock: [Enter to finish]

✓ Added 2 stocks!
```

### Option 5: Export List
Saves `stocks_list.txt` with all stocks for reference.

---

## 🔒 SAFETY FEATURES

### What's Protected:
✅ Main code can't be broken by friends
✅ Only JSON file is edited (safe)
✅ Validation in stock_manager.py
✅ Duplicate checking
✅ Error handling

### What Can Go Wrong:
⚠️ Friend adds invalid symbol (e.g., `FAKE.NS`)
   → Data fetch fails for that stock only
   → Other stocks work fine

⚠️ Friend misspells sector
   → No problem, just cosmetic
   → Can fix later

⚠️ JSON syntax error (manual edit)
   → stock_manager.py shows error
   → Fix JSON syntax
   → All code still safe

---

## 📈 SCALING TO 60-70 STOCKS

### Performance:
- **24 stocks**: ~2 minutes (current)
- **50 stocks**: ~4 minutes
- **70 stocks**: ~6 minutes

With `max_workers=7`, speeds up to:
- **50 stocks**: ~2.5 minutes
- **70 stocks**: ~3.5 minutes

### Excel Size:
- 70 stocks × 30 days × 27 slots = ~56,700 cells
- Excel handles this easily

### Tips:
1. Increase `max_workers` for speed:
   ```python
   populate_modular.py  # Edit max_workers=7 or 10
   ```

2. Batch by date range:
   ```bash
   # Fetch one week at a time
   python populate_modular.py 01-01-2026 07-01-2026
   python populate_modular.py 08-01-2026 14-01-2026
   ```

---

## 🛠️ TROUBLESHOOTING

### "No stocks loaded"
- Check `stocks_config.json` exists
- Run `python stock_manager.py` to verify stocks
- Make sure JSON syntax is correct

### "Stock not in Excel"
- You added stock to config but didn't recreate Excel
- Run: `python setup_excel.py`
- Then: `python populate_modular.py`

### "Invalid symbol"
- Check NSE website for correct symbol
- Must end with `.NS` (NSE) or `.BO` (BSE)
- Example: `RELIANCE.NS` not `RELIANCE`

### Friend broke JSON file
- JSON is strict about syntax
- Common errors:
  - Missing comma between entries
  - Missing quotes around strings
  - Extra comma at end
- Use online JSON validator or stock_manager.py

---

## 📋 STOCK SYMBOL FORMAT

### Correct Format:
```
RELIANCE.NS   ← NSE (National Stock Exchange)
RELIANCE.BO   ← BSE (Bombay Stock Exchange)
```

### Where to Find Symbols:
1. **NSE Website**: nseindia.com
2. **Yahoo Finance**: finance.yahoo.com
3. **Google**: Search "RELIANCE stock symbol NSE"

### Common Symbols:
```
Banking:
  HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, AXISBANK.NS

IT:
  TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS

Auto:
  TATAMOTORS.NS, MARUTI.NS, BAJAJ-AUTO.NS

Energy:
  RELIANCE.NS, ONGC.NS, BPCL.NS

Pharma:
  SUNPHARMA.NS, DRREDDY.NS, CIPLA.NS
```

---

## 🎓 BEST PRACTICES

### For You (Admin):
1. **Keep backup** of stocks_config.json
2. **Test new stocks** before bulk adding
3. **Run setup_excel.py** after any stock changes
4. **Set max_workers** based on internet speed
5. **Monitor fetch progress** for errors

### For Your Friends:
1. **Verify symbol** before adding (check Yahoo Finance)
2. **Use stock_manager.py** instead of editing JSON
3. **Tell admin** after adding stocks
4. **Don't delete** stocks others are using
5. **Export list** before major changes

---

## 🔄 TYPICAL WORKFLOW EXAMPLE

### Week 1: Initial Setup (You)
```bash
python stock_manager.py  # Add 24 stocks
python setup_excel.py    # Create Excel
python populate_modular.py  # Fetch data
```

### Week 2: Friends Add Stocks
```bash
# Friend A adds 5 stocks via stock_manager.py
# Friend B adds 3 stocks via stock_manager.py
# They tell you: "We added 8 stocks"
```

### Week 2: You Update System
```bash
python setup_excel.py    # Recreate Excel (now 32 stocks)
python populate_modular.py  # Fetch data for all 32
```

### Week 3: Regular Updates
```bash
# Daily or weekly:
python populate_modular.py --today  # Just today
# or
python populate_modular.py  # Entire date range
```

---

## 💡 ADVANCED TIPS

### 1. Organize by Sector
Edit JSON to group stocks:
```json
{
  "stocks": [
    {"symbol": "HDFCBANK.NS", "sector": "Banking"},
    {"symbol": "ICICIBANK.NS", "sector": "Banking"},
    {"symbol": "SBIN.NS", "sector": "Banking"},
    {"symbol": "TCS.NS", "sector": "IT"},
    {"symbol": "INFY.NS", "sector": "IT"}
  ]
}
```

### 2. Different Config Files
For different portfolios:
```bash
# Tech portfolio
STOCKS_CONFIG_FILE='tech_stocks.json' python populate_modular.py

# Banking portfolio
STOCKS_CONFIG_FILE='bank_stocks.json' python populate_modular.py
```

### 3. Automated Daily Updates
Create a batch file (Windows) or cron job (Linux):
```bash
# daily_update.bat (Windows)
python populate_modular.py --today

# or cron (Linux)
0 16 * * 1-5 /path/to/python /path/to/populate_modular.py --today
```

---

## ✅ SUMMARY

**For Your Friends:**
- Use `stock_manager.py` to add stocks
- Simple, safe, no code knowledge needed
- Tell you when done

**For You:**
- Run `setup_excel.py` when stocks change
- Run `populate_modular.py` to fetch data
- Analyze the data in Excel

**Benefits:**
- ✅ Code stays safe
- ✅ Friends can contribute
- ✅ Easy to scale to 60-70 stocks
- ✅ No programming needed for stock management
- ✅ Clear separation of responsibilities

**Your goal achieved:** You focus on analysis, friends help with stock selection!

---

Need help? Common commands:
```bash
python stock_manager.py          # Manage stocks
python setup_excel.py            # Create Excel
python populate_modular.py       # Fetch data
python populate_modular.py --today  # Just today
```

Happy Trading! 📈📊
