# Stock Screener Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         EVERY SATURDAY                           │
│                         10:00 AM UTC                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     GITHUB ACTIONS                               │
│  (Free cloud automation - no computer needed)                    │
│                                                                   │
│  1. Triggers workflow automatically                              │
│  2. Sets up Python environment                                   │
│  3. Installs dependencies (yfinance, pandas)                     │
│  4. Runs screener.py                                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SCREENER.PY                                 │
│                                                                   │
│  FOR EACH REGION:                                                │
│  ┌──────────────────────────────────────────────────┐           │
│  │ 1. Load tickers from file                        │           │
│  │    • russell1000_tickers.txt                     │           │
│  │    • tsx_composite_tickers.txt                   │           │
│  │    • ftse_allshare_tickers.txt                   │           │
│  │    • stoxx600_tickers.txt                        │           │
│  │                                                   │           │
│  │ 2. For each ticker:                              │           │
│  │    ├─> Download 52 weeks of price data (yfinance)│           │
│  │    ├─> Calculate 52-week high & low              │           │
│  │    ├─> Check if within 3% threshold              │           │
│  │    └─> Add to results if match found             │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                   │
│  3. Format results into HTML email                               │
│  4. Send via Gmail SMTP                                          │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL REPORT                                  │
│              barracudacapital@gmail.com                          │
│                                                                   │
│  ┌────────────────────────────────────────────┐                 │
│  │ Weekly Stock Screener - February 03, 2026  │                 │
│  │                                             │                 │
│  │ US (Russell 1000)                           │                 │
│  │ ├─ 52-Week Highs: 23 stocks                │                 │
│  │ │  AAPL $185.25 | High: $185.50 | -0.13%   │                 │
│  │ │  MSFT $425.80 | High: $428.00 | -0.51%   │                 │
│  │ │  ...                                      │                 │
│  │ └─ 52-Week Lows: 15 stocks                 │                 │
│  │    INTC $18.45 | Low: $18.20 | +1.37%      │                 │
│  │    ...                                      │                 │
│  │                                             │                 │
│  │ Canada (TSX Composite)                      │                 │
│  │ ├─ 52-Week Highs: ...                      │                 │
│  │ └─ 52-Week Lows: ...                       │                 │
│  │                                             │                 │
│  │ [Same for UK and Europe]                   │                 │
│  └────────────────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘

DATA FLOW:
═══════════

Ticker Files → yfinance API → Price Analysis → Email Report
   (GitHub)      (Free)        (Python)         (Gmail)

COST: $0 (Everything is free!)

REQUIREMENTS:
═════════════
✓ GitHub account (free)
✓ Gmail account (you have: barracudacapital@gmail.com)
✓ Gmail app password (one-time setup)
✓ Ticker lists (provided with samples, expand as needed)
```

## Key Features

### ✅ Fully Automated
- No manual work required after setup
- Runs every Saturday automatically
- No computer needs to be turned on

### ✅ Free Forever
- GitHub Actions: 2,000 minutes/month (free tier)
- This uses ~5-10 minutes/week = 40 minutes/month
- Well within free limits

### ✅ Easy to Customize
- Change schedule: Edit cron expression
- Change threshold: Edit one line (threshold = 0.03)
- Add regions: Create new ticker file
- Modify email format: Edit HTML template

### ✅ Reliable
- GitHub Actions has 99.9% uptime
- Automatic retries on failure
- Email delivery confirmation

## Maintenance

### Zero Maintenance Required
Once set up, it runs forever automatically.

### Optional Updates
- Update ticker lists annually (indices change composition)
- Adjust threshold if needed
- Add more regions

## Security

### Secure by Design
- Gmail app password stored as encrypted GitHub Secret
- Never exposed in code or logs
- Only accessible to your workflows
- Can be revoked anytime from Google Account
