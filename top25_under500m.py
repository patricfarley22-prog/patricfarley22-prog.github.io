#!/usr/bin/env python3
"""
TOP 25 MEME COINS UNDER $500M
Fetches from CoinGecko and filters for market cap < $500M
"""

import requests
import json
import time
from datetime import datetime

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DATA_DIR = "meme_coin_data"

def fetch_coins():
    """Fetch top coins by market cap"""
    print("[1/2] Fetching coins from CoinGecko...")
    
    meme_keywords = ['doge','shib','pepe','floki','bonk','meme','wojak',
                     'troll','cat','inu','elon','frog','chad','based',
                     'dog','musk','pump','woof','meow','pop','dust',
                     'giga','zerebro','bitcoin','mascot','housecoin',
                     'omega','hachi','pengo','tokabu','wobbles','dowge']
    
    all_coins = []
    
    # Fetch multiple pages
    for page in range(1, 5):
        try:
            url = f"{COINGECKO_BASE}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': 250,
                'page': page,
                'sparkline': False
            }
            
            time.sleep(1.2)
            r = requests.get(url, params=params, timeout=15)
            
            if r.status_code == 200:
                coins = r.json()
                
                for c in coins:
                    name = (c.get('name', '') + ' ' + c.get('symbol', '')).lower()
                    
                    # Check if meme coin
                    is_meme = any(kw in name for kw in meme_keywords)
                    
                    # Also check if it's a known meme
                    symbol = c.get('symbol', '').upper()
                    if symbol in ['DOGE','SHIB','PEPE','FLOKI','BONK','WIF','BRETT',
                                  'POPCAT','MOG','BOME','MEW','PONKE','GIGA','TURBO',
                                  'BABYDOGE','KISHU','AKITA','SAITAMA','ELON']:
                        is_meme = True
                    
                    if is_meme:
                        mcap = c.get('market_cap', 0) or 0
                        if 0 < mcap < 500_000_000:
                            all_coins.append({
                                'symbol': symbol,
                                'name': c.get('name', ''),
                                'market_cap': mcap,
                                'price': c.get('current_price', 0),
                                'change_24h': c.get('price_change_percentage_24h', 0),
                                'change_7d': c.get('price_change_percentage_7d', 0),
                                'volume_24h': c.get('total_volume', 0),
                                'circulating_supply': c.get('circulating_supply', 0),
                                'total_supply': c.get('total_supply', 0),
                                'ath': c.get('ath', 0),
                                'ath_change': c.get('ath_change_percentage', 0),
                                'image': c.get('image', ''),
                                'id': c.get('id', '')
                            })
                
                print(f"  Page {page}: {len(coins)} coins checked")
            elif r.status_code == 429:
                print("  Rate limit hit, waiting 60s...")
                time.sleep(60)
                continue
            else:
                print(f"  Error {r.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")
            continue
    
    # Sort by market cap
    all_coins.sort(key=lambda x: x['market_cap'], reverse=True)
    
    return all_coins[:25]

def display_coins(coins):
    if not coins:
        print("No coins found")
        return
    
    print("\n" + "=" * 80)
    print(f"TOP {len(coins)} MEME COINS UNDER $500M")
    print("=" * 80)
    
    print(f"\n{'#':<4} {'Symbol':<10} {'Name':<22} {'MCap':<12} {'Price':<12} {'24h':<8} {'7d':<8}")
    print("-" * 80)
    
    for i, c in enumerate(coins, 1):
        mcap = c['market_cap'] / 1_000_000
        print(f"{i:<4} {c['symbol']:<10} {c['name'][:20]:<22} ${mcap:<11.2f}M ${c['price']:<11.6f} "
              f"{c['change_24h'] or 0:<+7.1f}% {c['change_7d'] or 0:<+7.1f}%")
    
    # Breakdown
    nano = [c for c in coins if c['market_cap'] < 10_000_000]
    micro = [c for c in coins if 10_000_000 <= c['market_cap'] < 50_000_000]
    small = [c for c in coins if 50_000_000 <= c['market_cap'] < 100_000_000]
    mid = [c for c in coins if 100_000_000 <= c['market_cap'] < 500_000_000]
    
    print(f"\n{'='*80}")
    print("BREAKDOWN:")
    print(f"  Nano (<$10M): {len(nano)}")
    print(f"  Micro ($10-50M): {len(micro)}")
    print(f"  Small ($50-100M): {len(small)}")
    print(f"  Mid ($100-500M): {len(mid)}")
    
    print(f"\n{'='*80}")
    print("TOP PICKS:")
    
    # Best 24h performers
    best_24h = sorted([c for c in coins if c['change_24h']], key=lambda x: x['change_24h'] or 0, reverse=True)[:5]
    if best_24h:
        print("\n  Best 24h:")
        for c in best_24h:
            print(f"    {c['symbol']}: {c['change_24h']:+.1f}%")
    
    # Worst 24h (potential dips)
    worst_24h = sorted([c for c in coins if c['change_24h']], key=lambda x: x['change_24h'] or 0)[:5]
    if worst_24h:
        print("\n  Worst 24h (dip buys):")
        for c in worst_24h:
            print(f"    {c['symbol']}: {c['change_24h']:+.1f}%")

def main():
    print("\nTop 25 Meme Coins Under $500M")
    print("=" * 80)
    
    coins = fetch_coins()
    display_coins(coins)
    
    # Save
    import os
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/top25_under500m.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "count": len(coins),
            "coins": coins
        }, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Saved: {DATA_DIR}/top25_under500m.json")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
