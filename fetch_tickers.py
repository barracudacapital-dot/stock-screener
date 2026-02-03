"""
Helper script to fetch ticker lists from various sources.
Run this locally to populate your ticker files.

Note: This requires additional packages:
pip install beautifulsoup4 lxml
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_russell1000_tickers():
    """
    Get Russell 1000 tickers from iShares ETF holdings
    """
    print("Fetching Russell 1000 tickers...")
    
    # iShares Russell 1000 ETF (IWB) holdings
    url = "https://www.ishares.com/us/products/239707/ishares-russell-1000-etf/1467271812596.ajax?tab=all&fileType=csv"
    
    try:
        df = pd.read_csv(url, skiprows=10)  # Skip header rows
        tickers = df['Ticker'].dropna().unique().tolist()
        
        # Filter out non-stock entries
        tickers = [t for t in tickers if isinstance(t, str) and t.strip() and t != '-']
        
        print(f"Found {len(tickers)} Russell 1000 tickers")
        return tickers
    except Exception as e:
        print(f"Error fetching Russell 1000: {e}")
        return []

def get_tsx_composite_tickers():
    """
    Get TSX Composite tickers
    Note: You'll need to manually download from tsx.com or use a data provider
    """
    print("TSX Composite tickers need to be manually obtained from:")
    print("https://www.tsx.com/listings/current-listed-companies")
    print("Download CSV and add .TO suffix to each ticker")
    return []

def get_ftse_allshare_tickers():
    """
    Get FTSE All-Share tickers
    Note: You'll need to manually download from data provider
    """
    print("FTSE All-Share tickers need to be manually obtained from:")
    print("https://www.londonstockexchange.com/indices/ftse-all-share")
    print("Download constituents and add .L suffix to each ticker")
    return []

def get_stoxx600_tickers():
    """
    Get STOXX 600 tickers
    Note: You'll need to manually download from stoxx.com
    """
    print("STOXX 600 tickers need to be manually obtained from:")
    print("https://www.stoxx.com/index-details?symbol=SXXP")
    print("Download constituents with appropriate country suffixes")
    return []

def save_tickers_to_file(tickers, filename):
    """Save tickers to file"""
    with open(filename, 'w') as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")
    print(f"Saved {len(tickers)} tickers to {filename}")

def main():
    print("=" * 60)
    print("Ticker List Fetcher")
    print("=" * 60)
    
    # Russell 1000 (can be automated)
    russell_tickers = get_russell1000_tickers()
    if russell_tickers:
        save_tickers_to_file(russell_tickers, 'russell1000_tickers.txt')
    
    print("\n" + "=" * 60)
    
    # Other indices (manual process)
    print("\nFor other indices, you'll need to:")
    print("1. Visit the links provided above")
    print("2. Download the constituent lists")
    print("3. Format them with appropriate suffixes:")
    print("   - Canada: .TO (e.g., RY.TO)")
    print("   - UK: .L (e.g., SHEL.L)")
    print("   - France: .PA (e.g., MC.PA)")
    print("   - Germany: .DE (e.g., SAP.DE)")
    print("   - Netherlands: .AS (e.g., ASML.AS)")
    print("   - Switzerland: .SW (e.g., NESN.SW)")
    print("   - Sweden: .ST (e.g., VOLV-B.ST)")
    print("   - Denmark: .CO (e.g., NOVO-B.CO)")
    print("4. Save to respective ticker files")
    
    get_tsx_composite_tickers()
    print()
    get_ftse_allshare_tickers()
    print()
    get_stoxx600_tickers()

if __name__ == "__main__":
    main()
