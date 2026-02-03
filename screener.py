import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time

# Stock universe by region
STOCK_UNIVERSE = {
    'US': 'russell1000_tickers_corrected.txt',
    'Canada': 'tsx_composite_tickers.txt', 
    'UK': 'ftse_allshare_tickers.txt',
    'Europe': 'stoxx600_tickers.txt'
}

def get_tickers_from_file(filename):
    """Read tickers from file"""
    try:
        with open(filename, 'r') as f:
            tickers = [line.strip() for line in f 
                      if line.strip() and not line.strip().startswith('#')]
        return tickers
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return []

def calculate_52week_high_low(ticker, threshold=0.03):
    """
    Check if stock is within threshold of 52-week high or low
    Returns: ('high', price, 52w_high, percentage) or ('low', price, 52w_low, percentage) or None
    """
    try:
        stock = yf.Ticker(ticker)
        # Get 1 year of historical data
        hist = stock.history(period="1y")
        
        if hist.empty or len(hist) < 50:  # Need reasonable amount of data
            return None
            
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Calculate distance from highs/lows
        distance_from_high = (high_52w - current_price) / high_52w
        distance_from_low = (current_price - low_52w) / low_52w if low_52w > 0 else float('inf')
        
        # Check if within threshold of 52-week high
        if distance_from_high <= threshold:
            pct_from_high = ((current_price / high_52w) - 1) * 100
            return ('high', current_price, high_52w, pct_from_high)
        
        # Check if within threshold of 52-week low
        if distance_from_low <= threshold:
            pct_from_low = ((current_price / low_52w) - 1) * 100
            return ('low', current_price, low_52w, pct_from_low)
        
        return None
        
    except Exception as e:
        print(f"Error processing {ticker}: {str(e)}")
        return None

def screen_region(region_name, tickers, threshold=0.03):
    """Screen all tickers in a region"""
    print(f"\nScreening {region_name}...")
    
    highs = []
    lows = []
    
    for i, ticker in enumerate(tickers):
        if i % 50 == 0:
            print(f"  Progress: {i}/{len(tickers)}")
        
        result = calculate_52week_high_low(ticker, threshold)
        
        if result:
            signal_type, current, level, pct = result
            stock_info = {
                'Ticker': ticker,
                'Price': f"${current:.2f}",
                '52W Level': f"${level:.2f}",
                'Distance': f"{pct:+.2f}%"
            }
            
            if signal_type == 'high':
                highs.append(stock_info)
            else:
                lows.append(stock_info)
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    return highs, lows

def create_email_body(results):
    """Create HTML email body with results"""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            h3 {{ color: #7f8c8d; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th {{ background-color: #3498db; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .high {{ color: #27ae60; font-weight: bold; }}
            .low {{ color: #e74c3c; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Weekly Stock Screener - {datetime.now().strftime('%B %d, %Y')}</h1>
        <p>Stocks within 3% of 52-week highs and lows</p>
    """
    
    for region, (highs, lows) in results.items():
        html += f"<h2>{region}</h2>"
        
        if highs:
            html += f"""
            <h3 class="high">52-Week Highs ({len(highs)} stocks)</h3>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Current Price</th>
                    <th>52W High</th>
                    <th>Distance</th>
                </tr>
            """
            for stock in highs[:20]:  # Limit to top 20
                html += f"""
                <tr>
                    <td><b>{stock['Ticker']}</b></td>
                    <td>{stock['Price']}</td>
                    <td>{stock['52W Level']}</td>
                    <td class="high">{stock['Distance']}</td>
                </tr>
                """
            html += "</table>"
        else:
            html += "<p>No stocks at 52-week highs</p>"
        
        if lows:
            html += f"""
            <h3 class="low">52-Week Lows ({len(lows)} stocks)</h3>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Current Price</th>
                    <th>52W Low</th>
                    <th>Distance</th>
                </tr>
            """
            for stock in lows[:20]:  # Limit to top 20
                html += f"""
                <tr>
                    <td><b>{stock['Ticker']}</b></td>
                    <td>{stock['Price']}</td>
                    <td>{stock['52W Level']}</td>
                    <td class="low">{stock['Distance']}</td>
                </tr>
                """
            html += "</table>"
        else:
            html += "<p>No stocks at 52-week lows</p>"
    
    html += """
    </body>
    </html>
    """
    return html

def send_email(subject, body_html, to_emails, from_email, password):
    """Send email via Gmail to multiple recipients"""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    
    # Handle single email or list of emails
    if isinstance(to_emails, str):
        to_emails = [to_emails]
    
    msg['To'] = ', '.join(to_emails)
    
    html_part = MIMEText(body_html, 'html')
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(from_email, password)
        server.sendmail(from_email, to_emails, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {', '.join(to_emails)}")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def main():
    print("=" * 50)
    print("Weekly Stock Screener")
    print("=" * 50)
    
    # Get credentials from environment variables
    gmail_user = os.environ.get('GMAIL_USER', 'barracudacapital@gmail.com')
    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
    
    if not gmail_password:
        print("ERROR: GMAIL_APP_PASSWORD environment variable not set")
        return
    
    # Recipients - always include both addresses
    recipients = [gmail_user, 'eraats@hotmail.com']
    print(f"Will send to: {', '.join(recipients)}")
    
    threshold = 0.03  # 3% threshold
    all_results = {}
    
    # Screen each region
    for region, ticker_file in STOCK_UNIVERSE.items():
        tickers = get_tickers_from_file(ticker_file)
        
        if not tickers:
            print(f"No tickers found for {region}")
            all_results[region] = ([], [])
            continue
        
        highs, lows = screen_region(region, tickers, threshold)
        all_results[region] = (highs, lows)
        
        print(f"{region}: {len(highs)} at highs, {len(lows)} at lows")
    
    # Create and send email
    email_body = create_email_body(all_results)
    subject = f"Stock Screener Results - {datetime.now().strftime('%B %d, %Y')}"
    
    send_email(
        subject=subject,
        body_html=email_body,
        to_emails=recipients,
        from_email=gmail_user,
        password=gmail_password
    )
    
    print("\nScreening complete!")

if __name__ == "__main__":
    main()
