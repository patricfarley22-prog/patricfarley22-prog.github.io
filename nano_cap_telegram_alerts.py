#!/usr/bin/env python3
"""
NANO-CAP TELEGRAM ALERTS
Send screener results to your Telegram via OpenClaw
Uses your existing bot token
"""

import json
import os
from datetime import datetime
from typing import List, Dict

DATA_DIR = "meme_coin_data"

# Your Telegram config from TOOLS.md
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = "6643728142"  # Your Telegram ID

def load_screened_results():
    filepath = f"{DATA_DIR}/nano_cap_screened.json"
    if os.path.exists(filepath):
        with open(filepath) as f:
            data = json.load(f)
            return data.get('results', [])
    return []

def load_social_results():
    filepath = f"{DATA_DIR}/social_tracking.json"
    if os.path.exists(filepath):
        with open(filepath) as f:
            data = json.load(f)
            return data.get('results', [])
    return []

def format_telegram_message(screened, social):
    merged = {}
    for s in screened:
        merged[s['coin']['symbol']] = {'screened': s, 'social': None}
    for soc in social:
        if soc['symbol'] in merged:
            merged[soc['symbol']]['social'] = soc
    
    lines = [
        "NANO-CAP SCREENER ALERTS",
        f"Time: {datetime.now().strftime('%H:%M %m/%d')}",
        "",
        f"Screened: {len(screened)} coins",
        ""
    ]
    
    watch_coins = [s for s in screened if s['verdict'] == 'WATCH']
    if watch_coins:
        lines.extend(["WATCH LIST:", ""])
        for r in watch_coins[:5]:
            coin = r['coin']
            soc = merged.get(coin['symbol'], {}).get('social', {})
            lines.extend([
                f"  {coin['symbol']} (Score: {r['combined_score']:.1f})",
                f"    24h: {coin['change_24h']:+.1f}% | 7d: {coin['change_7d']:+.1f}%",
                f"    Social: {soc.get('verdict', 'N/A')} ({soc.get('organic_score', 0):.0f}%)",
                ""
            ])
    
    all_alerts = []
    for r in screened:
        all_alerts.extend(r.get('alerts', []))
    
    if all_alerts:
        from collections import Counter
        alert_counts = Counter(all_alerts)
        lines.extend(["ALERTS:", ""])
        for alert, count in alert_counts.most_common():
            lines.append(f"  - {alert}: {count} coins")
        lines.append("")
    
    passed = len([s for s in screened if s['verdict'] == 'PASS'])
    failed = len([s for s in screened if s['verdict'] == 'FAIL'])
    lines.extend([
        "SUMMARY:",
        f"  Pass: {passed} | Watch: {len(watch_coins)} | Fail: {failed}",
        "",
        "Run /screener for full details"
    ])
    
    return "\n".join(lines)

def send_telegram_alert(message):
    import urllib.request
    import urllib.parse
    
    if not TELEGRAM_BOT_TOKEN:
        print("No Telegram bot token configured")
        print("Set TELEGRAM_BOT_TOKEN environment variable")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }).encode()
        
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result.get('ok', False)
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def print_alert(message):
    print("\n" + "=" * 60)
    print("TELEGRAM ALERT (Console Fallback)")
    print("=" * 60)
    print(message)
    print("=" * 60)

def main():
    print("Nano-Cap Telegram Alerts")
    print("=" * 60)
    
    screened = load_screened_results()
    social = load_social_results()
    
    if not screened:
        print("No screener results found. Run nano_cap_screener.py first.")
        return
    
    message = format_telegram_message(screened, social)
    
    print("\nSending to Telegram...")
    sent = send_telegram_alert(message)
    
    if sent:
        print("[OK] Alert sent to Telegram!")
    else:
        print("[FAIL] Telegram send failed")
        print("\nDisplaying in console instead:")
        print_alert(message)
    
    with open(f"{DATA_DIR}/telegram_alerts.json", "a") as f:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "sent": sent,
            "message_preview": message[:200] + "...",
            "coins_count": len(screened)
        }
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"\nLog saved: {DATA_DIR}/telegram_alerts.json")

if __name__ == "__main__":
    main()
