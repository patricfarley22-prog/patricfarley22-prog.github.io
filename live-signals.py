#!/usr/bin/env python3
"""
LIVE QUANTUM SIGNALS
Generates real-time signals for meme coins
"""

import requests
import subprocess
import json
import os
from datetime import datetime

class LiveSignals:
    def __init__(self):
        self.data_dir = 'meme_coin_data'
    
    def fetch_dexscreener(self, ca):
        try:
            response = requests.get(f'https://api.dexscreener.com/latest/dex/tokens/{ca}', timeout=10)
            data = response.json()
            pair = data.get('pairs', [{}])[0]
            return {
                'price': float(pair.get('priceUsd', 0)),
                'mcap': float(pair.get('marketCap', 0)),
                'volume': float(pair.get('volume', {}).get('h24', 0)),
                'change24h': float(pair.get('priceChange', {}).get('h24', 0)),
                'change1h': float(pair.get('priceChange', {}).get('h1', 0)),
                'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN').upper()
            }
        except:
            return None
    
    def run_quantum(self, data):
        args = [
            str(data['change24h'] / 100),
            str(data['volume'] / 1_000_000),
            '0.5', '0', '0.6', '0.55', '0.45',
            str(min(data['liquidity'] / 50000, 1)),
            '0.5',
            str(min(data['volume'] / 10_000_000, 1))
        ]
        
        try:
            result = subprocess.run(
                ['python', 'quantum_analyzer.py'] + args,
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                output = result.stdout
                start = output.find('{')
                end = output.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(output[start:end+1])
            return {'signal': 'ERROR', 'confidence': 0}
        except:
            return {'signal': 'ERROR', 'confidence': 0}
    
    def generate_live_signals(self, coins):
        print("=" * 80)
        print("LIVE QUANTUM SIGNALS")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        results = []
        
        for symbol, ca in coins.items():
            print(f"\nFetching {symbol}...", end=" ")
            data = self.fetch_dexscreener(ca)
            
            if not data:
                print("FAILED")
                continue
            
            print(f"${data['price']:.8f}")
            
            quantum = self.run_quantum(data)
            signal = quantum.get('signal', 'UNKNOWN')
            confidence = quantum.get('confidence', 0)
            
            result = {
                'symbol': symbol,
                'price': data['price'],
                'mcap': data['mcap'],
                'change24h': data['change24h'],
                'volume': data['volume'],
                'signal': signal,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            
            status = "BUY" if 'BUY' in signal else "SELL" if 'SELL' in signal else "NEUTRAL"
            emoji = "+" if status == "BUY" else "-" if status == "SELL" else "="
            
            print(f"  {emoji} Signal: {signal} ({confidence*100:.1f}%)")
            print(f"  24h Change: {data['change24h']:+.2f}%")
            print(f"  Volume: ${data['volume']/1000000:.2f}M")
            print(f"  Market Cap: ${data['mcap']/1000000:.2f}M")
        
        # Rank by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        print("\n" + "=" * 80)
        print("TOP SIGNALS (Ranked by Confidence)")
        print("=" * 80)
        
        for i, r in enumerate(results[:10], 1):
            arrow = "^" if 'BUY' in r['signal'] else "v" if 'SELL' in r['signal'] else "-"
            print(f"{i}. {arrow} {r['symbol']}: {r['signal']} ({r['confidence']*100:.1f}%)")
            print(f"   Price: ${r['price']:.8f} | 24h: {r['change24h']:+.2f}%")
        
        # Save
        filepath = os.path.join(self.data_dir, 'live-signals.json')
        with open(filepath, 'w') as f:
            json.dump({'timestamp': datetime.now().isoformat(), 'signals': results}, f, indent=2)
        
        print(f"\nSaved to: {filepath}")
        return results


def main():
    signals = LiveSignals()
    
    coins = {
        'TROLL': '5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2',
        'DOWGE': 'DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump',
        'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
        'WIF': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
        'FLOKI': 'FLOKI',
        'WOBBLES': '9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump',
        'PENGO': 'F2k82EcxLtzekq1bfoGVdgp6EXZ5dLT1jE7g3LvQpump',
        'TOKABU': 'H8xQ6poBjB9DTPMDTKWzWPrnxu4bDEhybxiouF8Ppump',
        'OMEGAX': '4Aar9R14YMbEie6yh8WcH1gWXrBtfucoFjw6SpjXpump',
        'HACHI': 'AsrtqZiNYt3c6nNCtkj7abUrVc8APsFF37Wffq45rkVh'
    }
    
    signals.generate_live_signals(coins)


if __name__ == "__main__":
    main()
