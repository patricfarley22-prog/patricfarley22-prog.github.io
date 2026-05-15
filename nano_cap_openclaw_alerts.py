#!/usr/bin/env python3
"""
NANO-CAP OPENCLAW ALERTS
Send alerts via OpenClaw system
Uses sessions_send for Telegram delivery
"""

import json
import os
from datetime import datetime
from typing import List, Dict

DATA_DIR = "meme_coin_data"

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

def format_alert(screened, social):
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
    
    # Top picks by score
    top_coins = sorted(screened, key=lambda x: x['combined_score'], reverse=True)[:3]
    if top_coins:
        lines.extend(["TOP PICKS:", ""])
        for r in top_coins:
            coin = r['coin']
            lines.extend([
                f"  {coin['symbol']} (Score: {r['combined_score']:.1f})",
                f"    Price: ${coin['price']:.8f} | MCap: ${coin['market_cap']/1_000_000:.2f}M",
                f"    24h: {coin['change_24h']:+.1f}% | 7d: {coin['change_7d']:+.1f}%",
                f"    Tier: {r['tier']} | Verdict: {r['verdict']}",
                ""
            ])
    
    # Alerts
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
    
    # Summary
    passed = len([s for s in screened if s['verdict'] == 'PASS'])
    failed = len([s for s in screened if s['verdict'] == 'FAIL'])
    watch = len([s for s in screened if s['verdict'] == 'WATCH'])
    
    lines.extend([
        "SUMMARY:",
        f"  Pass: {passed} | Watch: {watch} | Fail: {failed}",
        ""
    ])
    
    return "\n".join(lines)

def save_openclaw_alert(message):
    """Save alert for OpenClaw pickup"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    alert_file = f"{DATA_DIR}/openclaw_alerts.json"
    
    alerts = []
    if os.path.exists(alert_file):
        with open(alert_file) as f:
            for line in f:
                if line.strip():
                    alerts.append(json.loads(line))
    
    new_alert = {
        "timestamp": datetime.now().isoformat(),
        "type": "NANO_CAP_SCREEN",
        "message": message,
        "channel": "telegram",
        "chat_id": "6643728142"
    }
    
    alerts.append(new_alert)
    
    # Keep last 50 alerts
    alerts = alerts[-50:]
    
    with open(alert_file, "w") as f:
        for a in alerts:
            f.write(json.dumps(a) + "\n")
    
    print(f"Alert saved to: {alert_file}")
    print(f"Total alerts in queue: {len(alerts)}")
    return alert_file

def main():
    print("Nano-Cap OpenClaw Alerts")
    print("=" * 60)
    
    screened = load_screened_results()
    social = load_social_results()
    
    if not screened:
        print("No screener results found. Run nano_cap_screener.py first.")
        return
    
    message = format_alert(screened, social)
    
    print("\nFormatting alert for OpenClaw...")
    print("=" * 60)
    print(message)
    print("=" * 60)
    
    # Save for OpenClaw
    alert_file = save_openclaw_alert(message)
    
    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. OpenClaw will pick up alerts from meme_coin_data/openclaw_alerts.json")
    print("2. Or use sessions_send to deliver directly to Telegram")
    print("3. Set up cron job to run hourly for continuous monitoring")
    print("=" * 60)

if __name__ == "__main__":
    main()
