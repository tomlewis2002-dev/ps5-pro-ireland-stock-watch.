import json, os, re, urllib.request, urllib.error
from pathlib import Path

# Conservative, best-effort checks of public product pages.
# No login, CAPTCHA bypass, proxy rotation, or paywall circumvention.
SHOPS = [
    {"id":"smyths","name":"Smyths Toys","url":"https://www.smythstoys.com/ie/en-ie/gaming-and-tech/playstation-5/playstation-5-consoles/playstation-5-pro-consoles/c/playstation-5-pro-consoles"},
    {"id":"currys","name":"Currys Ireland","url":"https://www.currys.ie/products/sony-playstation-5-pro-10272138.html"},
    {"id":"did","name":"DID Electrical","url":"https://www.did.ie/products/sony-playstation-5-pro-gaming-console-white-black-9024408"},
    {"id":"powercity","name":"Power City","url":"https://powercity.ie/product/9024408"},
    {"id":"harvey","name":"Harvey Norman","url":"https://www.harveynorman.ie/collections/playstation"},
    {"id":"amazon","name":"Amazon Ireland","url":"https://www.amazon.ie/s?k=PS5+Pro+console"},
]

STATE_FILE = Path("stock_state.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IrelandPS5ProAvailabilityCheck/1.0; +https://github.com/)"}

def classify(html):
    t = re.sub(r"\s+", " ", html.lower())
    # Treat explicit unavailable wording as out of stock first.
    out_patterns = [
        r"\bout of stock\b", r"\bsold out\b", r"\bcurrently unavailable\b",
        r"\bnot available\b", r"\bnotify me\b", r"\bemail me when available\b"
    ]
    if any(re.search(p, t) for p in out_patterns):
        return "out"
    in_patterns = [
        r"\bin stock\b", r"\bavailable to order\b", r"\bavailable online\b",
        r"\badd to basket\b", r"\badd to cart\b"
    ]
    if any(re.search(p, t) for p in in_patterns):
        return "in"
    return "unknown"

def fetch(shop):
    req = urllib.request.Request(shop["url"], headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            if r.status != 200:
                return "unknown", f"HTTP {r.status}"
            body = r.read(2_000_000).decode("utf-8", errors="ignore")
            return classify(body), "page checked"
    except Exception as e:
        return "unknown", type(e).__name__

def send_ntfy(title, message, url):
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic:
        raise RuntimeError("Missing NTFY_TOPIC secret")
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh").rstrip("/")
    data = message.encode("utf-8")
    req = urllib.request.Request(
        f"{server}/{topic}", data=data, method="POST",
        headers={
            "Title": title,
            "Priority": "high",
            "Tags": "video_game,shopping_bags",
            "Click": url,
            "Actions": f"view,Open retailer,{url}"
        }
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        if r.status >= 300:
            raise RuntimeError(f"ntfy returned HTTP {r.status}")

def main():
    old = {}
    if STATE_FILE.exists():
        try:
            old = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            old = {}
    new = {}
    for shop in SHOPS:
        status, detail = fetch(shop)
        previous = old.get(shop["id"], "unknown")
        new[shop["id"]] = status
        print(f'{shop["name"]}: {status} ({detail})')
        # Only notify on a transition into a possible in-stock state.
        if status == "in" and previous != "in":
            send_ntfy(
                f'Possible PS5 Pro stock: {shop["name"]}',
                f'Possible availability detected at {shop["name"]}. Confirm live stock, price and Dublin collection/delivery before travelling or paying. This may be a false positive.',
                shop["url"]
            )
    STATE_FILE.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
