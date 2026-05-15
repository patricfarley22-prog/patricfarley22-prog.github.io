#!/usr/bin/env python3
"""
COLLECT 90+ DAYS HISTORY FOR ALL MEME COINS
Uses CoinGecko + DexScreener for comprehensive data
"""

import requests
import json
import os
import time
from datetime import datetime

class HistoryCollector:
    def __init__(self):
        self.data_dir = 'meme_coin_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # All meme coins to track
        self.coins = {
            # CoinGecko IDs
            'bonk': 'BONK',
            'floki': 'FLOKI', 
            'pepe': 'PEPE',
            'shiba-inu': 'SHIB',
            'dogecoin': 'DOGE',
            
            # Solana contract addresses (for DexScreener)
            'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK-SOL',
            'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm': 'WIF',
            '5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2': 'TROLL',
            'DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump': 'DOWGE',
            '9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump': 'WOBBLES',
            'F2k82EcxLtzekq1bfoGVdgp6EXZ5dLT1jE7g3LvQpump': 'PENGO',
            'H8xQ6poBjB9DTPMDTKWzWPrnxu4bDEhybxiouF8Ppump': 'TOKABU',
            '4Aar9R14YMbEie6yh8WcH1gWXrBtfucoFjw6SpjXpump': 'OMEGAX',
            'AsrtqZiNYt3c6nNCtkj7abUrVc8APsFF37Wffq45rkVh': 'HACHI',
            'CXLnKtCzbdgtdH94LUwgiNkdB6esa6ry2Vqrdi1DVfhm': 'DUST',
            'VCRvsrGNycLHKspffE2dNw1vpFPwA8xQPKbgJeiftVV': 'ROYAL',
        }
    
    def fetch_coingecko_history(self, coin_id, days=90):
        """Fetch historical data from CoinGecko"""
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': days, 'interval': 'daily'}
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 429:
                print(f"  Rate limited, waiting...")
                time.sleep(60)
                return self.fetch_coingecko_history(coin_id, days)
            
            response.raise_for_status()
            data = response.json()
            
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            mcaps = data.get('market_caps', [])
            
            history = []
            for i in range(len(prices)):
                history.append({
                    'date': datetime.fromtimestamp(prices[i][0]/1000).strftime('%Y-%m-%d'),
                    'price': prices[i][1],
                    'volume': volumes[i][1] if i < len(volumes) else 0,
                    'market_cap': mcaps[i][1] if i < len(mcaps) else 0
                })
            
            return history
        except Exception as e:
            print(f"  CoinGecko error: {e}")
            return None
    
    def fetch_dexscreener_history(self, ca):
        """Fetch current data from DexScreener (no history API, just current)"""
        url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pair = data.get('pairs', [{}])[0]
            if not pair:
                return None
            
            return [{
                'date': datetime.now().strftime('%Y-%m-%d'),
                'price': float(pair.get('priceUsd', 0)),
                'volume': float(pair.get('volume', {}).get('h24', 0)),
                'market_cap': float(pair.get('marketCap', 0)),
                'source': 'dexscreener'
            }]
        except Exception as e:
            print(f"  DexScreener error: {e}")
            return None
    
    def collect_all(self):
        """Collect data for all coins"""
        print("=" * 80)
        print("COLLECTING HISTORICAL DATA FOR ALL MEME COINS")
        print("=" * 80)
        print()
        
        results = {}
        
        for coin_id, symbol in self.coins.items():
            print(f"Fetching {symbol}...", end=" ")
            
            # Try CoinGecko first (for coin IDs without dashes)
            if '-' in coin_id or len(coin_id) < 40:
                history = self.fetch_coingecko_history(coin_id, days=90)
                if history:
                    print(f"OK - {len(history)} days (CoinGecko)")
                else:
                    print("Failed (CoinGecko)")
            else:
                # Solana contract - use DexScreener
                history = self.fetch_dexscreener_history(coin_id)
                if history:
                    print(f"OK - Current data (DexScreener)")
                else:
                    print("Failed (DexScreener)")
            
            if history:
                # Calculate metrics
                metrics = self.calculate_metrics(history)
                
                # Save
                data = {
                    'symbol': symbol,
                    'coin_id': coin_id,
                    'last_updated': datetime.now().isoformat(),
                    'metrics': metrics,
                    'history': history[-60:]  # Keep last 60 days
                }
                
                filepath = os.path.join(self.data_dir, f'{symbol}_history.json')
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                
                results[symbol] = data
            
            time.sleep(2)  # Rate limiting
        
        return results
    
    def calculate_metrics(self, history):
        """Calculate metrics"""
        if not history:
            return {}
        
        latest = history[-1]
        prices = [h['price'] for h in history]
        
        # Changes
        price_7d = history[-8]['price'] if len(history) >= 8 else latest['price']
        price_30d = history[-31]['price'] if len(history) >= 31 else latest['price']
        
        return {
            'current_price': latest['price'],
            'current_mcap': latest.get('market_cap', 0),
            'current_volume': latest.get('volume', 0),
            'price_change_7d': ((latest['price'] - price_7d) / price_7d * 100) if price_7d > 0 else 0,
            'price_change_30d': ((latest['price'] - price_30d) / price_30d * 100) if price_30d > 0 else 0,
            'max_price_30d': max(prices[-30:]) if len(prices) >= 30 else max(prices),
            'min_price_30d': min(prices[-30:]) if len(prices) >= 30 else min(prices),
            'data_points': len(history),
            'source': latest.get('source', 'coingecko')
        }
    
    def display_summary(self, results):
        """Display summary"""
        print("\n" + "=" * 80)
        print("COLLECTION COMPLETE")
        print("=" * 80)
        
        print(f"\n{'Symbol':<10} {'Days':<6} {'Price':<14} {'7d':<8} {'30d':<8} {'Source':<12}")
        print("-" * 80)
        
        for symbol, data in results.items():
            m = data['metrics']
            source = m.get('source', 'coingecko')
            print(f"{symbol:<10} {m['data_points']:<6} ${m['current_price']:<13.8f} "
                  f"{m['price_change_7d']:<+7.1f}% {m['price_change_30d']:<+7.1f}% {source:<12}")


if __name__ == "__main__":
    collector = HistoryCollector()
    results = collector.collect_all()
    collector.display_summary(results)
