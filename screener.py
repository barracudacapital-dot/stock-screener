
import yfinance as yf
import pandas as pd
import multiprocessing as mp
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time

# -----------------------------
# Performance Settings
# -----------------------------
CHUNK_SIZE = 150
MAX_WORKERS = 4   # Safe for Yahoo Finance


# -----------------------------
# Stock universe files
# -----------------------------
STOCK_UNIVERSE = {
    'US': 'russell1000_tickers_corrected.txt',
    'Canada': 'tsx_composite_tickers.txt',
    'UK': 'ftse_allshare_tickers.txt',
    'Europe': 'stoxx600_tickers.txt'
}


# -----------------------------
# Utilities
# -----------------------------
def get_tickers_from_file(filename):
    try:
        with open(filename, 'r') as f:
            tickers = [line.strip() for line in f
                       if line.strip() and not line.strip().startswith('#')]
        return tickers
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return []


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


# -----------------------------
# Core Screening Logic
# -----------------------------
def process_chunk(args):
    tickers, threshold = args
    highs = []
    lows = []

    try:
        data = yf.download(
            tickers,
            period="1y",
            group_by="ticker",
            auto_adjust=False,
            threads=False,
            progress=False
        )

        for ticker in tickers:
            try:
                if ticker not in data.columns.levels[0]:
                    continue

                hist = data[ticker].dropna()
                if len(hist) < 50:
                    continue

                current_price = hist['Close'].iloc[-1]
                high_52w = hist['High'].max()
                low_52w = hist['Low'].min()

                distance_from_high = (high_52w - current_price) / high_52w
                distance_from_low = (
                    (current_price - low_52w) / low_52w
                    if low_52w > 0 else float("inf")
                )

                stock_info = {
                    'ticker': ticker,
                    'company_name': ticker,
                    'price': round(current_price, 2),
                    'return_3m': None,
                    'return_6m': None
                }

                if len(hist) >= 63:
                    price_3m = hist['Close'].iloc[-63]
                    stock_info['return_3m'] = round(
                        ((current_price / price_3m) - 1) * 100, 2
                    )

                if len(hist) >= 126:
                    price_6m = hist['Close'].iloc[-126]
                    stock_info['return_6m'] = round(
                        ((current_price / price_6m) - 1) * 100, 2
                    )

                if distance_from_high <= threshold:
                    stock_info['level'] = round(high_52w, 2)
                    stock_info['distance'] = round(
                        ((current_price / high_52w) - 1) * 100, 2
                    )
                    highs.append(stock_info)

                elif distance_from_low <= threshold:
                    stock_info['level'] = round(low_52w, 2)
                    stock_info['distance'] = round(
                        ((current_price / low_52w) - 1) * 100, 2
                    )
                    lows.append(stock_info)

            except Exception:
                continue

    except Exception:
        pass

    return highs, lows


def screen_region(region_name, tickers, threshold=0.03):
    print(f"\nScreening {region_name}...")
    print(f"Total tickers: {len(tickers)}")

    chunks = list(chunk_list(tickers, CHUNK_SIZE))

    with mp.Pool(processes=MAX_WORKERS) as pool:
        results = pool.map(
            process_chunk,
            [(chunk, threshold) for chunk in chunks]
        )

    all_highs = []
    all_lows = []

    for highs, lows in results:
        all_highs.extend(highs)
        all_lows.extend(lows)

    print(f"{region_name}: {len(all_highs)} highs, {len(all_lows)} lows")

    time.sleep(3)

    return all_highs, all_lows


# -----------------------------
# Main
# -----------------------------
def main():
    print("=" * 50)
    print("Optimized Weekly Stock Screener")
    print("=" * 50)

    threshold = 0.03
    all_results = {}

    for region, ticker_file in STOCK_UNIVERSE.items():
        tickers = get_tickers_from_file(ticker_file)

        if not tickers:
            print(f"No tickers found for {region}")
            all_results[region] = ([], [])
            continue

        highs, lows = screen_region(region, tickers, threshold)
        all_results[region] = (highs, lows)

    print("\nScreening complete.")


if __name__ == "__main__":
    main()
