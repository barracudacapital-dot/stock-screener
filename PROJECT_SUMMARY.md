# Stock Screener Project - Complete Package

## 📦 What's Included

### Core Files
1. **screener.py** - Main Python script that performs the screening
2. **requirements.txt** - Python dependencies
3. **.github/workflows/screener.yml** - GitHub Actions automation

### Ticker Files (with samples)
4. **russell1000_tickers.txt** - US stocks
5. **tsx_composite_tickers.txt** - Canadian stocks
6. **ftse_allshare_tickers.txt** - UK stocks
7. **stoxx600_tickers.txt** - European stocks

### Documentation
8. **QUICKSTART.md** - 15-minute setup guide
9. **README.md** - Complete documentation
10. **ARCHITECTURE.md** - How it works diagram
11. **.gitignore** - Git configuration

### Helper Scripts
12. **fetch_tickers.py** - Helper to download ticker lists

## 🚀 Quick Setup (15 minutes)

### Step 1: Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Create app password for "Mail" / "Stock Screener"
3. Copy the 16-character password

### Step 2: GitHub Repository
1. Create new repo: https://github.com/new (name: `stock-screener`)
2. Upload all files from this folder
3. Add Secret: `GMAIL_APP_PASSWORD` = your app password

### Step 3: Test
1. Go to Actions tab
2. Run workflow manually
3. Check email in 2-5 minutes

## ✨ Features

- **Automated**: Runs every Saturday at 10 AM UTC
- **Free**: Uses GitHub Actions (2,000 free minutes/month)
- **Multi-Region**: US, Canada, UK, Europe
- **Customizable**: Easy to modify threshold, schedule, regions
- **Email Reports**: Clean HTML format with all results

## 📊 What It Screens

For each region, identifies stocks that are:
- Within 3% of 52-week HIGH
- Within 3% of 52-week LOW

### Indices Covered
- **US**: Russell 1000 (large-cap US stocks)
- **Canada**: TSX Composite (Canadian stocks)
- **UK**: FTSE All-Share (UK stocks)
- **Europe**: STOXX 600 (European stocks including Nordic)

## 📧 Email Report Format

```
Weekly Stock Screener - [Date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

US (Russell 1000)
━━━━━━━━━━━━━━
52-Week Highs (15 stocks)
┌────────────────────────────┐
│ AAPL  $185.25  (-0.13%)    │
│ MSFT  $425.80  (-0.51%)    │
└────────────────────────────┘

52-Week Lows (8 stocks)
┌────────────────────────────┐
│ INTC  $18.45  (+1.37%)     │
└────────────────────────────┘

[Repeated for each region]
```

## 🔧 Customization Options

### Change Schedule
Edit `.github/workflows/screener.yml`:
```yaml
cron: '0 10 * * 6'  # Saturday 10 AM UTC
```

### Change Threshold
Edit `screener.py`:
```python
threshold = 0.03  # 3% default
```

### Add More Stocks
Add tickers to the `.txt` files (one per line)

### Change Email Format
Modify `create_email_body()` function in `screener.py`

## 📈 Performance

- **Execution Time**: 2-10 minutes (depending on number of stocks)
- **Cost**: $0 (free tier)
- **Reliability**: 99.9% (GitHub Actions uptime)
- **Data Source**: yfinance (free, Yahoo Finance data)

## ⚠️ Important Notes

### Ticker List Population
The provided ticker files contain only ~25 sample tickers each. For full screening:
1. Download complete index constituent lists
2. Add proper suffixes:
   - US: no suffix (e.g., AAPL)
   - Canada: .TO (e.g., RY.TO)
   - UK: .L (e.g., SHEL.L)
   - Europe: .PA, .DE, .AS, .SW, .ST, .CO, etc.

### Data Limitations (Free Tier)
- yfinance is free but has rate limits
- May occasionally fail for some tickers
- Script includes 0.1s delay between tickers to avoid rate limiting
- Most reliable for major liquid stocks

### Gmail Requirements
- Must have 2-factor authentication enabled
- Must use App Password (not regular password)
- Regular Gmail sending limits apply (~500 emails/day)

## 🔒 Security

- Gmail password stored as encrypted GitHub Secret
- Never exposed in code or logs
- Can revoke app password anytime
- Repository can be private

## 📚 Documentation Files

- **QUICKSTART.md** - Start here for 15-min setup
- **README.md** - Comprehensive guide
- **ARCHITECTURE.md** - Visual explanation of how it works

## 🆘 Troubleshooting

**Email not working?**
→ Check Actions logs for errors
→ Verify GMAIL_APP_PASSWORD secret is correct
→ Check spam folder

**Workflow fails?**
→ Check Actions tab for error details
→ Verify all ticker files exist
→ Check ticker format (correct suffixes)

**Too slow?**
→ Reduce number of tickers
→ Increase delay between API calls
→ Consider paid data source

## 📞 Support

- Read QUICKSTART.md for setup
- Read README.md for detailed docs
- Check ARCHITECTURE.md to understand how it works
- Create GitHub issue for bugs

## 🎯 Next Steps

1. ✅ Follow QUICKSTART.md to set up
2. ✅ Test with sample tickers first
3. ✅ Populate full ticker lists
4. ✅ Customize schedule/threshold as needed
5. ✅ Enjoy automated weekly reports!

---

**Created for**: barracudacapital@gmail.com
**Date**: February 2026
**Version**: 1.0
**Cost**: Free Forever
