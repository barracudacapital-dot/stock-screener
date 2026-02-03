# Quick Start Guide

Follow these steps to get your stock screener running in 15 minutes.

## Step 1: Create Gmail App Password (5 minutes)

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled
3. Search for "App passwords" or go to https://myaccount.google.com/apppasswords
4. Create new app password:
   - App: Mail
   - Device: Other (Custom name) → "Stock Screener"
5. Click **Generate**
6. **COPY the 16-character password** (looks like: `xxxx xxxx xxxx xxxx`)
7. Keep this window open - you'll need it in Step 3

## Step 2: Create GitHub Repository (3 minutes)

1. Go to https://github.com/new
2. Repository name: `stock-screener`
3. Set to **Private** (recommended) or Public
4. Do NOT initialize with README (we have our own files)
5. Click **Create repository**

## Step 3: Add GitHub Secret (2 minutes)

1. In your new repository, click **Settings**
2. Left sidebar: **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GMAIL_APP_PASSWORD`
5. Value: Paste your 16-character app password from Step 1 (remove spaces)
6. Click **Add secret**

## Step 4: Upload Files to GitHub (3 minutes)

### Option A: Using GitHub Web Interface
1. In your repository, click **Add file** → **Upload files**
2. Drag and drop ALL files from the stock-screener folder
3. Commit message: "Initial commit"
4. Click **Commit changes**

### Option B: Using Git Command Line
```bash
cd stock-screener
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-screener.git
git push -u origin main
```

## Step 5: Test It! (2 minutes)

1. Go to **Actions** tab in your repository
2. Click **Weekly Stock Screener** workflow on the left
3. Click **Run workflow** (button on the right)
4. Select **main** branch
5. Click **Run workflow**
6. Wait 2-5 minutes for it to complete
7. Check your email: barracudacapital@gmail.com

## ✅ Done!

Your screener will now run automatically every Saturday at 10:00 AM UTC.

## Next Steps

### Customize Schedule
Edit `.github/workflows/screener.yml` to change the day/time:
```yaml
schedule:
  - cron: '0 10 * * 6'  # Saturday 10 AM UTC
```

Common times (all UTC):
- `'0 14 * * 6'` = Saturday 2 PM UTC (9 AM EST, 6 AM PST)
- `'0 16 * * 6'` = Saturday 4 PM UTC (11 AM EST, 8 AM PST)
- `'0 18 * * 5'` = Friday 6 PM UTC (1 PM EST, 10 AM PST)

### Populate Full Ticker Lists
The current files have only ~25 sample tickers per region. To screen full indices:

1. **Russell 1000**: Download from iShares IWB ETF holdings CSV
2. **TSX Composite**: Download from tsx.com/listings
3. **FTSE All-Share**: Download from index provider
4. **STOXX 600**: Download from stoxx.com

Replace the sample tickers in each `.txt` file with complete lists.

### Adjust Threshold
In `screener.py`, change the threshold:
```python
threshold = 0.03  # 3% (default)
threshold = 0.02  # 2% (stricter)
threshold = 0.05  # 5% (looser)
```

## Troubleshooting

**Email not received?**
- Check **Actions** tab → Latest run → Check for errors
- Verify secret is named exactly `GMAIL_APP_PASSWORD`
- Check spam folder in Gmail
- Try re-creating the app password

**Workflow failed?**
- Click on failed run in Actions tab
- Click on **screen-stocks** job
- Read error messages
- Common issues:
  - Missing ticker files
  - Invalid ticker symbols
  - Typo in secret name

**Need help?**
- Check full README.md for detailed documentation
- Create an issue in the repository
- Run locally first: `python screener.py` (after setting GMAIL_APP_PASSWORD env var)

## Security Note

Your Gmail app password is stored securely as a GitHub Secret and is never exposed in logs or code. Only your GitHub Actions workflows can access it.
