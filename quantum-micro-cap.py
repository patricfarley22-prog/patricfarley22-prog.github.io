#!/usr/bin/env python3
"""
QUANTUM MICRO-CAP SCANNER
Meme coins under $100M market cap with quantum signals
"""

import requests
import subprocess
import json
import os
import time
from datetime import datetime

class MicroCapScanner:
    def __init__(self):
        self.data_dir = 'meme_coin_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Sub-$100M meme coins (Solana ecosystem)
        self.micro_caps = {
            'DOWGE': {
                'ca': 'DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump',
                'category': 'meme'
            },
            'WOBBLES': {
                'ca': '9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump',
                'category': 'meme'
            },
            'PENGO': {
                'ca': 'F2k82EcxLtzekq1bfoGVdgp6EXZ5dLT1jE7g3LvQpump',
                'category': 'meme'
            },
            'TOKABU': {
                'ca': 'H8xQ6poBjB9DTPMDTKWzWPrnxu4bDEhybxiouF8Ppump',
                'category': 'meme'
            },
            'OMEGAX': {
                'ca': '4Aar9R14YMbEie6yh8WcH1gWXrBtfucoFjw6SpjXpump',
                'category': 'meme'
            },
            'HACHI': {
                'ca': 'AsrtqZiNYt3c6nNCtkj7abUrVc8APsFF37Wffq45rkVh',
                'category': 'meme'
            },
            'SPX': {
                'ca': 'J3NKxxXZcnchiMjMnb4LNbgytiW4tJd5b3a9RzQGfW',
                'category': 'meme'
            },
            'TURBO': {
                'ca': 'HPm3Uf2A9p8i2qKj8F6p3AqL2v8K9m5NqR3t7PqR2s',
                'category': 'meme'
            }
        }
    
    def fetch_dexscreener(self, ca):
        """Fetch real-time data from DexScreener"""
        try:
            response = requests.get(f'https://api.dexscreener.com/latest/dex/tokens/{ca}', timeout=10)
            data = response.json()
            pair = data.get('pairs', [{}])[0]
            
            if not pair or not pair.get('priceUsd'):
                return None
            
            return {
                'price': float(pair.get('priceUsd', 0)),
                'mcap': float(pair.get('marketCap', 0)),
                'volume_24h': float(pair.get('volume', {}).get('h24', 0)),
                'volume_1h': float(pair.get('volume', {}).get('h1', 0)),
                'change_24h': float(pair.get('priceChange', {}).get('h24', 0)),
                'change_1h': float(pair.get('priceChange', {}).get('h1', 0)),
                'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                'holders': int(pair.get('txns', {}).get('h24', {}).get('buys', 0) + pair.get('txns', {}).get('h24', {}).get('sells', 0)) if pair.get('txns') and pair.get('txns', {}).get('h24') else 0,
                'txns_24h': int(pair.get('txns', {}).get('h24', {}).get('buys', 0) + pair.get('txns', {}).get('h24', {}).get('sells', 0)) if pair.get('txns') and pair.get('txns', {}).get('h24') else 0,
                'symbol': pair.get('baseToken', {}).get('symbol', 'UNKNOWN').upper(),
                'name': pair.get('baseToken', {}).get('name', 'Unknown'),
                'chain': pair.get('chainId', 'unknown')
            }
        except Exception as e:
            print(f"    Error fetching: {e}")
            return None
    
    def run_quantum(self, data):
        """Run quantum analyzer on micro-cap data"""
        # Prepare features for quantum analyzer
        change_24h = data['change_24h'] / 100  # Convert to decimal
        volume_24h = data['volume_24h'] / 1_000_000  # In millions
        liquidity = min(data['liquidity'] / 50_000, 1)  # Normalized
        mcap_ratio = min(data['mcap'] / 100_000_000, 1)  # Under 100M = <1
        
        # Volatility proxy (1h vs 24h ratio)
        if abs(data['change_24h']) > 0:
            volatility = abs(data['change_1h']) / abs(data['change_24h'])
        else:
            volatility = 0.5
        
        args = [
            str(change_24h),
            str(volume_24h),
            '0.5',  # sentiment neutral
            '0',    # no news
            str(min(volatility * 2, 1)),  # volatility
            '0.55',  # correlation
            str(1 - mcap_ratio),  # micro-cap bias
            str(liquidity),
            '0.3',  # whale activity (micro-caps lower)
            str(min(data['volume_24h'] / 10_000_000, 1))
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
            return {'signal': 'ERROR', 'confidence': 0, 'entanglement': 0}
        except Exception as e:
            return {'signal': f'ERROR: {str(e)[:30]}', 'confidence': 0, 'entanglement': 0}
    
    def scan_all(self):
        """Scan all micro-cap coins"""
        print("=" * 80)
        print("QUANTUM MICRO-CAP SCANNER")
        print(f"Targeting: Coins under $100M market cap")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        results = []
        alerts = []
        
        for symbol, info in self.micro_caps.items():
            print(f"\n[{symbol}] Scanning...", end=" ")
            
            data = self.fetch_dexscreener(info['ca'])
            if not data:
                print("FAILED")
                continue
            
            print(f"OK | ${data['price']:.8f} | MCap: ${data['mcap']/1_000_000:.2f}M")
            
            # Skip if over $100M
            if data['mcap'] > 100_000_000:
                print(f"  SKIP: Market cap ${data['mcap']/1_000_000:.2f}M > $100M")
                continue
            
            # Run quantum analysis
            quantum = self.run_quantum(data)
            
            result = {
                'symbol': symbol,
                'name': data['name'],
                'price': data['price'],
                'mcap': data['mcap'],
                'volume_24h': data['volume_24h'],
                'change_24h': data['change_24h'],
                'change_1h': data['change_1h'],
                'liquidity': data['liquidity'],
                'signal': quantum.get('signal', 'UNKNOWN'),
                'confidence': quantum.get('confidence', 0),
                'entanglement': quantum.get('entanglement', 0),
                'category': info['category'],
                'timestamp': datetime.now().isoformat()
            }
            results.append(result)
            
            # Check for alerts (10% moves for micro-caps)
            if abs(data['change_24h']) >= 10:
                alert = {
                    'symbol': symbol,
                    'type': 'PRICE_SPIKE',
                    'severity': 'HIGH' if abs(data['change_24h']) > 20 else 'MEDIUM',
                    'change_24h': data['change_24h'],
                    'price': data['price'],
                    'signal': result['signal'],
                    'confidence': result['confidence']
                }
                alerts.append(alert)
                print(f"  ALERT: {alert['severity']} - {data['change_24h']:+.1f}% move!")
            
            # Display
            arrow = "+" if 'BUY' in result['signal'] else "-" if 'SELL' in result['signal'] else "="
            print(f"  {arrow} Signal: {result['signal']} ({result['confidence']*100:.1f}%)")
            print(f"  24h: {data['change_24h']:+.2f}% | 1h: {data['change_1h']:+.2f}%")
            print(f"  Vol: ${data['volume_24h']/1000000:.3f}M | Liq: ${data['liquidity']/1000:.1f}K")
            
            time.sleep(1)  # Rate limiting
        
        # Summary
        self.display_summary(results, alerts)
        
        # Save
        self.save_results(results, alerts)
        
        return results, alerts
    
    def display_summary(self, results, alerts):
        """Display scan summary"""
        print("\n" + "=" * 80)
        print("SCAN SUMMARY")
        print("=" * 80)
        
        if not results:
            print("No coins found under $100M")
            return
        
        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"\n{'#':<4} {'Symbol':<10} {'Signal':<8} {'Conf':<6} {'Price':<14} {'24h':<8} {'MCap':<10}")
        print("-" * 80)
        
        for i, r in enumerate(results[:15], 1):
            arrow = "^" if 'BUY' in r['signal'] else "v" if 'SELL' in r['signal'] else "-"
            print(f"{i:<4} {r['symbol']:<10} {arrow}{r['signal']:<7} {r['confidence']*100:<5.1f}% "
                  f"${r['price']:<13.8f} {r['change_24h']:<+7.1f}% ${r['mcap']/1_000_000:<9.2f}M")
        
        # Alerts
        if alerts:
            print(f"\n{'='*80}")
            print(f"ALERTS ({len(alerts)} triggered)")
            print(f"{'='*80}")
            for alert in alerts:
                severity_marker = "[!HIGH]" if alert['severity'] == 'HIGH' else "[*MED]"
                print(f"{severity_marker} {alert['symbol']}: {alert['change_24h']:+.1f}% | Signal: {alert['signal']} ({alert['confidence']*100:.1f}%)")
        
        # Signal counts
        buy_count = sum(1 for r in results if 'BUY' in r['signal'])
        sell_count = sum(1 for r in results if 'SELL' in r['signal'])
        hold_count = len(results) - buy_count - sell_count
        
        print(f"\nSignal Distribution:")
        print(f"  BUY: {buy_count} | SELL: {sell_count} | HOLD: {hold_count}")
    
    def save_results(self, results, alerts):
        """Save results to file"""
        filepath = os.path.join(self.data_dir, 'micro-cap-scan.json')
        data = {
            'timestamp': datetime.now().isoformat(),
            'criteria': 'under_100m_mcap',
            'total_scanned': len(self.micro_caps),
            'found': len(results),
            'alerts': len(alerts),
            'results': results,
            'alert_list': alerts
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nSaved to: {filepath}")
    
    def get_top_picks(self, results, min_confidence=0.40):
        """Get top picks for trading"""
        picks = [r for r in results if r['confidence'] >= min_confidence]
        
        # Sort: BUY signals first, then by confidence
        picks.sort(key=lambda x: (0 if 'BUY' in x['signal'] else 1, -x['confidence']))
        
        return picks[:5]


def main():
    scanner = MicroCapScanner()
    results, alerts = scanner.scan_all()
    
    # Get top picks
    top_picks = scanner.get_top_picks(results, min_confidence=0.35)
    
    if top_picks:
        print("\n" + "=" * 80)
        print("TOP PICKS (Confidence >= 35%)")
        print("=" * 80)
        
        for i, pick in enumerate(top_picks, 1):
            action = "BUY" if 'BUY' in pick['signal'] else "SELL" if 'SELL' in pick['signal'] else "WATCH"
            print(f"\n{i}. {pick['symbol']} - {action}")
            print(f"   Price: ${pick['price']:.8f}")
            print(f"   Market Cap: ${pick['mcap']/1_000_000:.2f}M")
            print(f"   Signal: {pick['signal']} ({pick['confidence']*100:.1f}% confidence)")
            print(f"   24h Change: {pick['change_24h']:+.2f}%")
            print(f"   Volume: ${pick['volume_24h']/1_000_000:.3f}M")


if __name__ == "__main__":
    main()
