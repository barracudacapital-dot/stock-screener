# Weekly Stock Screener

Automated stock screener that runs every Saturday to identify stocks within 3% of their 52-week highs and lows across multiple regions.

## Features

- **Regions Covered**: US (Russell 1000), Canada (TSX Composite), UK (FTSE All-Share), Europe (STOXX 600)
- **Automated Execution**: Runs every Saturday at 10:00 AM UTC via GitHub Actions
- **Email Reports**: Sends formatted HTML email with results
- **Free**: Completely free using GitHub Actions and yfinance

## Setup Instructions

### 1. Fork/Create Repository on GitHub

1. Create a new GitHub repository called `stock-screener`
2. Upload all files from this project to your repository

### 2. Set Up Gmail App Password

Since you're using `barracudacapital@gmail.com`, you need to create an App Password:

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Scroll down to **App passwords**
4. Click **App passwords**
5. Select **Mail** and **Other (Custom name)**
6. Name it "Stock Screener"
7. Click **Generate**
8. **Copy the 16-character password** (you'll need this next)

### 3. Add Secret to GitHub Repository

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GMAIL_APP_PASSWORD`
5. Value: Paste the 16-character app password from step 2
6. Click **Add secret**

### 4. Populate Ticker Files

The current ticker files contain only sample tickers. You need to populate them with complete lists:

#### Option A: Manual Population
Edit each file and add tickers (one per line):
- `russell1000_tickers.txt` - Add all Russell 1000 tickers
- `tsx_composite_tickers.txt` - Add all TSX tickers with `.TO` suffix
- `ftse_allshare_tickers.txt` - Add all FTSE tickers with `.L` suffix
- `stoxx600_tickers.txt` - Add all STOXX 600 tickers with appropriate suffixes

#### Option B: Use Data Provider
You can obtain ticker lists from:
- **Russell 1000**: https://www.ishares.com/us/products/239707/ishares-russell-1000-etf (download holdings)
- **TSX Composite**: https://www.tsx.com/listings/current-listed-companies (filter and format)
- **FTSE All-Share**: Similar approach using index provider websites
- **STOXX 600**: https://www.stoxx.com/index-details (download constituents)

**Important**: Ensure ticker symbols include the correct suffix for yfinance:
- US stocks: No suffix (e.g., `AAPL`)
- Canadian stocks: `.TO` suffix (e.g., `RY.TO`)
- UK stocks: `.L` suffix (e.g., `SHEL.L`)
- European stocks: Country-specific suffixes:
  - France: `.PA` (e.g., `MC.PA`)
  - Germany: `.DE` (e.g., `SAP.DE`)
  - Netherlands: `.AS` (e.g., `ASML.AS`)
  - Switzerland: `.SW` (e.g., `NESN.SW`)
  - Nordic: `.ST`, `.CO`, `.HE`, `.OL` (Stockholm, Copenhagen, Helsinki, Oslo)

### 5. Test the Workflow

1. Go to **Actions** tab in your GitHub repository
2. Click on **Weekly Stock Screener** workflow
3. Click **Run workflow** → **Run workflow** (manual trigger)
4. Wait for the workflow to complete
5. Check your email at barracudacapital@gmail.com

### 6. Schedule Configuration

The screener runs every Saturday at 10:00 AM UTC by default. To change the schedule:

1. Edit `.github/workflows/screener.yml`
2. Modify the cron expression:
   ```yaml
   schedule:
     - cron: '0 10 * * 6'  # Minute Hour Day Month DayOfWeek
   ```
   
**Cron Examples:**
- `'0 10 * * 6'` - 10:00 AM UTC every Saturday
- `'0 14 * * 6'` - 2:00 PM UTC every Saturday
- `'30 9 * * 6'` - 9:30 AM UTC every Saturday

**Timezone Note**: GitHub Actions uses UTC. Convert to your local timezone:
- EST/EDT: UTC - 5/4 hours
- PST/PDT: UTC - 8/7 hours
- CET/CEST: UTC + 1/2 hours

## File Structure

```
stock-screener/
├── .github/
│   └── workflows/
│       └── screener.yml           # GitHub Actions workflow
├── screener.py                    # Main Python script
├── requirements.txt               # Python dependencies
├── russell1000_tickers.txt        # US tickers
├── tsx_composite_tickers.txt      # Canadian tickers
├── ftse_allshare_tickers.txt      # UK tickers
├── stoxx600_tickers.txt           # European tickers
└── README.md                      # This file
```

## How It Works

1. **Every Saturday**: GitHub Actions triggers the workflow automatically
2. **Data Collection**: Script downloads 52-week price data for all tickers using yfinance
3. **Screening**: Identifies stocks within 3% of 52-week high or low
4. **Email Report**: Sends formatted HTML email with results organized by region

## Email Report Format

The email includes:
- Date of screening
- Results organized by region (US, Canada, UK, Europe)
- For each region:
  - List of stocks at 52-week highs (top 20)
  - List of stocks at 52-week lows (top 20)
  - Current price, 52-week level, and distance percentage

## Troubleshooting

### Email Not Received
- Check GitHub Actions logs in the **Actions** tab
- Verify `GMAIL_APP_PASSWORD` secret is set correctly
- Check spam folder
- Ensure 2-factor authentication is enabled on Gmail

### Workflow Failed
- Check the **Actions** tab for error logs
- Common issues:
  - Missing ticker files
  - Invalid ticker symbols
  - Rate limiting from yfinance (add delays in code)

### Too Many Tickers / Slow Execution
- GitHub Actions has a 6-hour timeout
- For large lists (1000+ tickers), consider:
  - Running in batches
  - Optimizing the code
  - Using paid data sources with faster APIs

## Customization

### Change Threshold
Edit `screener.py`:
```python
threshold = 0.03  # Change to 0.02 for 2%, 0.05 for 5%, etc.
```

### Add More Regions
1. Create new ticker file (e.g., `asia_tickers.txt`)
2. Add to `STOCK_UNIVERSE` dict in `screener.py`:
   ```python
   STOCK_UNIVERSE = {
       'US': 'russell1000_tickers.txt',
       'Asia': 'asia_tickers.txt',  # Add new region
       ...
   }
   ```

### Change Email Format
Modify the `create_email_body()` function in `screener.py` to customize HTML/styling.

## License

MIT License - Feel free to modify and use as needed.

## Support

For issues or questions, create an issue in the GitHub repository.
