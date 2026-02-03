import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
import json

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
    Returns: dict with stock data or None
    """
    try:
        stock = yf.Ticker(ticker)
        
        # Get company name
        try:
            company_name = stock.info.get('longName') or stock.info.get('shortName') or ticker
        except:
            company_name = ticker
        
        # Get 1 year of historical data
        hist = stock.history(period="1y")
        
        if hist.empty or len(hist) < 50:  # Need reasonable amount of data
            return None
            
        current_price = hist['Close'].iloc[-1]
        high_52w = hist['High'].max()
        low_52w = hist['Low'].min()
        
        # Calculate 3-month and 6-month returns
        return_3m = None
        return_6m = None
        
        if len(hist) >= 63:  # ~3 months of trading days
            price_3m_ago = hist['Close'].iloc[-63]
            return_3m = ((current_price / price_3m_ago) - 1) * 100
        
        if len(hist) >= 126:  # ~6 months of trading days
            price_6m_ago = hist['Close'].iloc[-126]
            return_6m = ((current_price / price_6m_ago) - 1) * 100
        
        # Calculate distance from highs/lows
        distance_from_high = (high_52w - current_price) / high_52w
        distance_from_low = (current_price - low_52w) / low_52w if low_52w > 0 else float('inf')
        
        # Check if within threshold of 52-week high
        if distance_from_high <= threshold:
            pct_from_high = ((current_price / high_52w) - 1) * 100
            return {
                'type': 'high',
                'company_name': company_name,
                'price': current_price,
                'level': high_52w,
                'distance': pct_from_high,
                'return_3m': return_3m,
                'return_6m': return_6m
            }
        
        # Check if within threshold of 52-week low
        if distance_from_low <= threshold:
            pct_from_low = ((current_price / low_52w) - 1) * 100
            return {
                'type': 'low',
                'company_name': company_name,
                'price': current_price,
                'level': low_52w,
                'distance': pct_from_low,
                'return_3m': return_3m,
                'return_6m': return_6m
            }
        
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
            stock_info = {
                'ticker': ticker,
                'company_name': result['company_name'],
                'price': round(result['price'], 2),
                'level': round(result['level'], 2),
                'distance': round(result['distance'], 2),
                'return_3m': round(result['return_3m'], 2) if result['return_3m'] is not None else None,
                'return_6m': round(result['return_6m'], 2) if result['return_6m'] is not None else None
            }
            
            if result['type'] == 'high':
                highs.append(stock_info)
            else:
                lows.append(stock_info)
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    return highs, lows

def create_dashboard_html(results):
    """Create interactive HTML dashboard with all results"""
    
    # Calculate statistics
    total_highs = sum(len(highs) for highs, _ in results.values())
    total_lows = sum(len(lows) for _, lows in results.values())
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Screener Results - {datetime.now().strftime('%B %d, %Y')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .date {{
            color: #7f8c8d;
            font-size: 1.1em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .region-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        h2 {{
            color: #2c3e50;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .category {{
            margin: 30px 0;
        }}
        
        h3 {{
            color: #34495e;
            font-size: 1.3em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .badge {{
            background: #3498db;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: normal;
        }}
        
        .badge.high {{
            background: #27ae60;
        }}
        
        .badge.low {{
            background: #e74c3c;
        }}
        
        .search-box {{
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 20px;
            transition: border-color 0.3s;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            background: white;
        }}
        
        th {{
            background: #3498db;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        
        th:hover {{
            background: #2980b9;
        }}
        
        th.high {{
            background: #27ae60;
        }}
        
        th.high:hover {{
            background: #229954;
        }}
        
        th.low {{
            background: #e74c3c;
        }}
        
        th.low:hover {{
            background: #c0392b;
        }}
        
        th.sortable::after {{
            content: ' ↕';
            opacity: 0.5;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .ticker-cell {{
            font-weight: bold;
            color: #2c3e50;
            font-size: 1.1em;
        }}
        
        .company-cell {{
            color: #7f8c8d;
            font-size: 0.95em;
            max-width: 250px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .price-cell {{
            color: #34495e;
        }}
        
        .distance-high {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .distance-low {{
            color: #e74c3c;
            font-weight: bold;
        }}
        
        .no-results {{
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-style: italic;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }}
        
        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                grid-template-columns: 1fr;
            }}
            
            table {{
                font-size: 0.9em;
            }}
            
            th, td {{
                padding: 8px 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Stock Screener Dashboard</h1>
            <div class="date">{datetime.now().strftime('%A, %B %d, %Y')}</div>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_highs}</div>
                    <div class="stat-label">Stocks at 52W Highs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_lows}</div>
                    <div class="stat-label">Stocks at 52W Lows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_highs + total_lows}</div>
                    <div class="stat-label">Total Signals</div>
                </div>
            </div>
        </div>
"""
    
    # Add each region
    for region, (highs, lows) in results.items():
        html += f"""
        <div class="region-section">
            <h2>{region}</h2>
"""
        
        # 52-Week Highs
        if highs:
            html += f"""
            <div class="category">
                <h3>
                    <span>52-Week Highs</span>
                    <span class="badge high">{len(highs)} stocks</span>
                </h3>
                <input type="text" class="search-box" placeholder="Search tickers or companies..." 
                       onkeyup="filterTable(this, '{region}-highs-table')">
                <table id="{region}-highs-table">
                    <thead>
                        <tr>
                            <th class="high sortable" onclick="sortTable('{region}-highs-table', 0)">Ticker</th>
                            <th class="high sortable" onclick="sortTable('{region}-highs-table', 1)">Company</th>
                            <th class="high sortable" onclick="sortTable('{region}-highs-table', 2)">Current Price</th>
                            <th class="high sortable" onclick="sortTable('{region}-highs-table', 3)">52W High</th>
                            <th class="high sortable" onclick="sortTable('{region}-highs-table', 4)">Distance</th>
                            <th class="high sortable" onclick="sortTable('{region}-highs-table', 5)">3M Return</th>
                            <th class="high sortable" onclick="sortTable('{region}-highs-table', 6)">6M Return</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for stock in highs:
                return_3m_display = f"{stock['return_3m']:+.2f}%" if stock['return_3m'] is not None else "N/A"
                return_6m_display = f"{stock['return_6m']:+.2f}%" if stock['return_6m'] is not None else "N/A"
                return_3m_class = "distance-high" if stock['return_3m'] and stock['return_3m'] > 0 else "distance-low" if stock['return_3m'] and stock['return_3m'] < 0 else ""
                return_6m_class = "distance-high" if stock['return_6m'] and stock['return_6m'] > 0 else "distance-low" if stock['return_6m'] and stock['return_6m'] < 0 else ""
                
                html += f"""
                        <tr>
                            <td class="ticker-cell">{stock['ticker']}</td>
                            <td class="company-cell" title="{stock['company_name']}">{stock['company_name']}</td>
                            <td class="price-cell">${stock['price']:.2f}</td>
                            <td class="price-cell">${stock['level']:.2f}</td>
                            <td class="distance-high">{stock['distance']:+.2f}%</td>
                            <td class="{return_3m_class}">{return_3m_display}</td>
                            <td class="{return_6m_class}">{return_6m_display}</td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
            </div>
"""
        else:
            html += '<div class="no-results">No stocks at 52-week highs</div>'
        
        # 52-Week Lows
        if lows:
            html += f"""
            <div class="category">
                <h3>
                    <span>52-Week Lows</span>
                    <span class="badge low">{len(lows)} stocks</span>
                </h3>
                <input type="text" class="search-box" placeholder="Search tickers or companies..." 
                       onkeyup="filterTable(this, '{region}-lows-table')">
                <table id="{region}-lows-table">
                    <thead>
                        <tr>
                            <th class="low sortable" onclick="sortTable('{region}-lows-table', 0)">Ticker</th>
                            <th class="low sortable" onclick="sortTable('{region}-lows-table', 1)">Company</th>
                            <th class="low sortable" onclick="sortTable('{region}-lows-table', 2)">Current Price</th>
                            <th class="low sortable" onclick="sortTable('{region}-lows-table', 3)">52W Low</th>
                            <th class="low sortable" onclick="sortTable('{region}-lows-table', 4)">Distance</th>
                            <th class="low sortable" onclick="sortTable('{region}-lows-table', 5)">3M Return</th>
                            <th class="low sortable" onclick="sortTable('{region}-lows-table', 6)">6M Return</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            for stock in lows:
                return_3m_display = f"{stock['return_3m']:+.2f}%" if stock['return_3m'] is not None else "N/A"
                return_6m_display = f"{stock['return_6m']:+.2f}%" if stock['return_6m'] is not None else "N/A"
                return_3m_class = "distance-high" if stock['return_3m'] and stock['return_3m'] > 0 else "distance-low" if stock['return_3m'] and stock['return_3m'] < 0 else ""
                return_6m_class = "distance-high" if stock['return_6m'] and stock['return_6m'] > 0 else "distance-low" if stock['return_6m'] and stock['return_6m'] < 0 else ""
                
                html += f"""
                        <tr>
                            <td class="ticker-cell">{stock['ticker']}</td>
                            <td class="company-cell" title="{stock['company_name']}">{stock['company_name']}</td>
                            <td class="price-cell">${stock['price']:.2f}</td>
                            <td class="price-cell">${stock['level']:.2f}</td>
                            <td class="distance-low">{stock['distance']:+.2f}%</td>
                            <td class="{return_3m_class}">{return_3m_display}</td>
                            <td class="{return_6m_class}">{return_6m_display}</td>
                        </tr>
"""
            html += """
                    </tbody>
                </table>
            </div>
"""
        else:
            html += '<div class="no-results">No stocks at 52-week lows</div>'
        
        html += """
        </div>
"""
    
    # Add JavaScript for sorting and filtering
    html += """
        <div class="footer">
            <p>Updated automatically every Saturday | Within 3% of 52-week levels</p>
        </div>
    </div>
    
    <script>
        function sortTable(tableId, column) {
            const table = document.getElementById(tableId);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                let aVal = a.cells[column].textContent.trim();
                let bVal = b.cells[column].textContent.trim();
                
                // Remove $ and % for numeric comparison
                aVal = aVal.replace(/[$%]/g, '');
                bVal = bVal.replace(/[$%]/g, '');
                
                // Try to parse as number
                const aNum = parseFloat(aVal);
                const bNum = parseFloat(bVal);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return bNum - aNum; // Descending for numbers
                }
                
                return aVal.localeCompare(bVal); // Ascending for strings
            });
            
            rows.forEach(row => tbody.appendChild(row));
        }
        
        function filterTable(input, tableId) {
            const filter = input.value.toUpperCase();
            const table = document.getElementById(tableId);
            const tbody = table.querySelector('tbody');
            const rows = tbody.querySelectorAll('tr');
            
            rows.forEach(row => {
                const ticker = row.cells[0].textContent.toUpperCase();
                row.style.display = ticker.includes(filter) ? '' : 'none';
            });
        }
    </script>
</body>
</html>
"""
    
    return html

def create_summary_email(results):
    """Create concise summary email with link to dashboard"""
    total_highs = sum(len(highs) for highs, _ in results.values())
    total_lows = sum(len(lows) for _, lows in results.values())
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; margin-bottom: 10px; }}
            .date {{ color: #7f8c8d; margin-bottom: 20px; }}
            .summary {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .stat {{ font-size: 2em; font-weight: bold; }}
            .label {{ font-size: 0.9em; opacity: 0.9; }}
            .region {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }}
            .region-name {{ font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
            .counts {{ color: #34495e; }}
            .high {{ color: #27ae60; font-weight: bold; }}
            .low {{ color: #e74c3c; font-weight: bold; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
            .button:hover {{ background: #764ba2; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Weekly Stock Screener</h1>
            <div class="date">{datetime.now().strftime('%A, %B %d, %Y')}</div>
            
            <div class="summary">
                <div class="stat">{total_highs + total_lows}</div>
                <div class="label">Total signals found</div>
            </div>
            
            <h2>Summary by Region</h2>
"""
    
    for region, (highs, lows) in results.items():
        html += f"""
            <div class="region">
                <div class="region-name">{region}</div>
                <div class="counts">
                    <span class="high">↑ {len(highs)} at 52W highs</span> | 
                    <span class="low">↓ {len(lows)} at 52W lows</span>
                </div>
            </div>
"""
    
    html += """
            <a href="https://barracudacapital-dot.github.io/stock-screener/" class="button">
                View Full Dashboard →
            </a>
            
            <p style="color: #7f8c8d; font-size: 0.9em; margin-top: 30px;">
                The dashboard contains ALL stocks found (no limits), with sortable tables and search functionality.
            </p>
        </div>
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
    
    # Recipients
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
    
    # Create dashboard HTML
    dashboard_html = create_dashboard_html(all_results)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    print("\n✅ Dashboard created: index.html")
    
    # Create and send summary email
    email_body = create_summary_email(all_results)
    subject = f"Stock Screener Results - {datetime.now().strftime('%B %d, %Y')}"
    
    send_email(
        subject=subject,
        body_html=email_body,
        to_emails=recipients,
        from_email=gmail_user,
        password=gmail_password
    )
    
    print("\n✅ Screening complete!")
    print("📊 View full results in index.html")

if __name__ == "__main__":
    main()
