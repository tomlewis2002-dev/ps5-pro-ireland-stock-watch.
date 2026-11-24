# PS5 Pro Ireland Stock Watch

A small, best-effort GitHub Actions checker for public PS5 Pro retailer pages, with push notifications through ntfy.

## Important limitations

- Retailer pages change frequently. This checks page text and can miss stock or produce false positives.
- A notification means **possible availability**, not confirmed stock. Open the retailer link and verify the exact console, price, delivery and Dublin collection.
- It does not bypass logins, CAPTCHAs, paywalls, bot protections, or access restrictions. If a retailer blocks automated requests, leave that source as unknown or remove it.
- Check each retailer's terms before enabling automated checks. Do not increase the frequency or evade technical restrictions.
- GitHub scheduled runs are not guaranteed to start at the exact minute.

## Setup

### 1. Create an ntfy topic

1. Install **ntfy** from Google Play on your Android phone.
2. Open the app and subscribe to a new topic with a long, hard-to-guess name (for example, a random string of at least 20 characters).
3. Keep the topic name private. ntfy.sh topics are public to anyone who knows the name; do not use a personal name or other identifying information.

### 2. Add this project to GitHub

1. On GitHub, create a new repository named `ps5-pro-ireland-stock-watch`.
2. Set it to **Private**.
3. Upload the files and folders from this project, preserving the `.github/workflows/stock-watch.yml` path.
4. In the repository, open **Settings → Secrets and variables → Actions → New repository secret**.
5. Add a secret named `NTFY_TOPIC` and paste the exact topic name you subscribed to in the ntfy app.

### 3. Enable and test

1. Open the repository's **Actions** tab and enable workflows if GitHub asks.
2. Select **PS5 Pro Ireland stock watch**.
3. Press **Run workflow** to test it manually.
4. Check the run log. A retailer may return `unknown` if it blocks automated requests or loads stock data only with JavaScript.

The scheduled check runs twice an hour. You can change the cron schedule in `.github/workflows/stock-watch.yml`, but keep checks respectful and infrequent.

## Retailers included

Smyths Toys, Currys Ireland, DID Electrical, Power City, Harvey Norman, and Amazon Ireland.
