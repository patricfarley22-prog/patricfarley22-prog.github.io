#!/usr/bin/env python3
"""
CORTEX DEEP VALUE ALPHA HUNTER
Finds 20-100x potential coins with real fundamentals
Target: Undervalued projects with explosive growth potential
"""

import requests
import json
import math
import time
from datetime import datetime
from typing import Dict, List, Optional

# Quantum
import pennylane as qml
from pennylane import numpy as np

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DEX_SCREENER = "https://api.dexscreener.com/latest/dex/search"
DATA_DIR = "meme_coin_data"

class DeepValueScreener:
    """Deep value crypto screener for 20-100x opportunities"""
    
    def __init__(self):
        self.dev = qml.device("default.qubit", wires=4, shots=1000)
        self.results = []
    
    def run_quantum(self, features):
        """Quantum circuit for deep value analysis"""
        @qml.qnode(self.dev)
        def circuit(f):
            # Encode undervaluation metrics
            for i, val in enumerate(f[:4]):
                qml.RY(val * np.pi, wires=i)
            
            # Entanglement = correlations between metrics
            qml.CNOT(wires=[0, 1])
            qml.CNOT(wires=[1, 2])
            qml.CNOT(wires=[2, 3])
            qml.CNOT(wires=[0, 3])
            
            # Growth potential layers
            for i in range(4):
                qml.RX(f[i % len(f)] * np.pi, wires=i)
                qml.RZ(f[(i+2) % len(f)] * np.pi, wires=i)
            
            # Measure growth probability
            return [qml.expval(qml.PauliZ(i)) for i in range(4)]
        
        return circuit(features)
    
    def fetch_coins(self) -> List[Dict]:
        """Fetch coins with 20-100x potential"""
        print("[1/6] Deep value scan: Finding undervalued gems...")
        
        coins = []
        
        # Scan pages 1-10 for $1M-$500M range
        for page in range(1, 11):
            try:
                url = f"{COINGECKO_BASE}/coins/markets"
                params = {
                    'vs_currency': 'usd',
                    'order': 'market_cap_asc',  # Start from smallest
                    'per_page': 250,
                    'page': page,
                    'sparkline': False
                }
                
                time.sleep(1.5)
                r = requests.get(url, params=params, timeout=15)
                
                if r.status_code == 200:
                    data = r.json()
                    for c in data:
                        mcap = c.get('market_cap', 0) or 0
                        volume = c.get('total_volume', 0) or 0
                        
                        # Target: $1M-$500M with room for 20-100x
                        if 1_000_000 <= mcap <= 500_000_000:
                            # Calculate potential metrics
                            ath = c.get('ath', 0) or 0
                            price = c.get('current_price', 0) or 0
                            ath_change = c.get('ath_change_percentage', 0) or 0
                            
                            # 20-100x potential from current price to ATH or beyond
                            if ath > 0 and price > 0:
                                from_ath = ath / price  # How many x to ATH
                            else:
                                from_ath = 0
                            
                            coins.append({
                                'symbol': c.get('symbol', '').upper(),
                                'name': c.get('name', ''),
                                'market_cap': mcap,
                                'price': price,
                                'volume_24h': volume,
                                'change_24h': c.get('price_change_percentage_24h', 0) or 0,
                                'change_7d': c.get('price_change_percentage_7d', 0) or 0,
                                'change_30d': c.get('price_change_percentage_30d', 0) or 0,
                                'ath': ath,
                                'ath_change': ath_change,
                                'from_ath': from_ath,
                                'circulating_supply': c.get('circulating_supply', 0),
                                'total_supply': c.get('total_supply', 0),
                                'liquidity': volume,  # Proxy
                                'id': c.get('id', '')
                            })
                    
                    print(f"  Page {page}: {len(data)} scanned")
                elif r.status_code == 429:
                    print("  Rate limit - waiting 60s...")
                    time.sleep(60)
            except Exception as e:
                print(f"  Error page {page}: {e}")
        
        return coins
    
    def score_deep_value(self, coins: List[Dict]) -> List[Dict]:
        """Score based on 20-100x potential"""
        print("\n[2/6] Scoring for 20-100x potential...")
        
        for c in coins:
            scores = {}
            
            # UNDervaluation Score (0-100)
            # Deeper from ATH = more undervalued = more upside
            ath_change = c.get('ath_change', 0)
            if -95 <= ath_change <= -80:
                scores['undervalued'] = 95  # Deep value
            elif -80 < ath_change <= -60:
                scores['undervalued'] = 85
            elif -60 < ath_change <= -40:
                scores['undervalued'] = 75
            elif -40 < ath_change <= -20:
                scores['undervalued'] = 60
            else:
                scores['undervalued'] = 30  # Not very undervalued
            
            # Market Cap Size (smaller = more upside)
            mcap = c['market_cap']
            if mcap < 5_000_000:
                scores['size'] = 100  # Micro = huge potential
            elif mcap < 20_000_000:
                scores['size'] = 90
            elif mcap < 50_000_000:
                scores['size'] = 80
            elif mcap < 100_000_000:
                scores['size'] = 70
            else:
                scores['size'] = 50  # Still room but less
            
            # Volume Activity (real interest)
            if c['market_cap'] > 0:
                vol_ratio = (c['volume_24h'] / c['market_cap']) * 100
            else:
                vol_ratio = 0
            
            if vol_ratio > 50:
                scores['activity'] = 100  # Hot
            elif vol_ratio > 20:
                scores['activity'] = 80
            elif vol_ratio > 10:
                scores['activity'] = 60
            elif vol_ratio > 5:
                scores['activity'] = 40
            else:
                scores['activity'] = 20  # Dead
            
            # Momentum (early stage)
            chg_24h = c['change_24h']
            chg_7d = c['change_7d']
            
            if 5 < chg_24h < 30 and chg_7d > 0:
                scores['momentum'] = 90  # Early pump, still room
            elif 0 < chg_24h < 5:
                scores['momentum'] = 70  # Starting
            elif -10 < chg_24h < 0:
                scores['momentum'] = 60  # Dip, potential reversal
            elif chg_24h > 50:
                scores['momentum'] = 40  # Already pumped
            else:
                scores['momentum'] = 30
            
            # Recovery Potential (how many x to ATH)
            from_ath = c.get('from_ath', 0)
            if from_ath >= 100:
                scores['recovery'] = 100  # 100x to ATH = massive potential
            elif from_ath >= 50:
                scores['recovery'] = 90
            elif from_ath >= 20:
                scores['recovery'] = 80
            elif from_ath >= 10:
                scores['recovery'] = 70
            elif from_ath >= 5:
                scores['recovery'] = 60
            else:
                scores['recovery'] = 40
            
            # 30-day trend (building or dying)
            chg_30d = c.get('change_30d', 0) or 0
            if chg_30d > 100:
                scores['trend'] = 85  # Strong uptrend
            elif chg_30d > 50:
                scores['trend'] = 75
            elif chg_30d > 0:
                scores['trend'] = 65
            elif chg_30d > -30:
                scores['trend'] = 50  # Correcting
            else:
                scores['trend'] = 30  # Downtrend
            
            # Liquidity check (can you actually buy/sell)
            liquidity = c.get('liquidity', 0)
            if liquidity > 1_000_000:
                scores['liquidity'] = 80  # Good
            elif liquidity > 500_000:
                scores['liquidity'] = 60
            elif liquidity > 100_000:
                scores['liquidity'] = 40
            else:
                scores['liquidity'] = 20  # Hard to trade
            
            # Calculate total weighted score
            weights = {
                'undervalued': 0.25,  # Most important
                'size': 0.20,         # Smaller = more upside
                'recovery': 0.20,     # X potential to ATH
                'activity': 0.15,     # Real volume
                'momentum': 0.10,     # Early stage
                'trend': 0.05,        # Building
                'liquidity': 0.05    # Can trade
            }
            
            total = sum(scores[k] * weights[k] for k in weights)
            c['scores'] = scores
            c['total_score'] = total
            c['vol_mcap_ratio'] = vol_ratio
        
        # Sort by score
        coins.sort(key=lambda x: x['total_score'], reverse=True)
        return coins
    
    def filter_high_potential(self, coins: List[Dict]) -> List[Dict]:
        """Filter for actual 20-100x potential"""
        print("\n[3/6] Filtering for 20-100x candidates...")
        
        filtered = []
        for c in coins:
            # Must have:
            # 1. Score > 60 (strong fundamentals)
            # 2. Recovery potential > 10x (to ATH)
            # 3. Some volume (not dead)
            # 4. Market cap under $500M
            
            if (c['total_score'] >= 60 and 
                c.get('from_ath', 0) >= 10 and
                c['vol_mcap_ratio'] >= 2 and
                c['market_cap'] <= 500_000_000):
                filtered.append(c)
        
        print(f"  {len(filtered)}/{len(coins)} have 20-100x potential")
        return filtered
    
    def run_quantum_analysis(self, coins: List[Dict]) -> List[Dict]:
        """Run quantum on top candidates"""
        print("\n[4/6] Running PennyLane quantum analysis...")
        
        top15 = coins[:15]
        
        for c in top15:
            symbol = c['symbol']
            
            # Build quantum features
            f1 = min(1.0, c['scores']['undervalued'] / 100)  # Undervaluation
            f2 = min(1.0, c['scores']['size'] / 100)          # Size
            f3 = min(1.0, c['scores']['recovery'] / 100)      # Recovery
            f4 = min(1.0, c['scores']['activity'] / 100)     # Activity
            
            features = [f1, f2, f3, f4]
            
            try:
                expvals = self.run_quantum(features)
                avg_exp = sum(expvals) / len(expvals)
                confidence = (avg_exp + 1) / 2
                
                if confidence > 0.70:
                    signal = "STRONG BUY"
                elif confidence > 0.60:
                    signal = "BUY"
                elif confidence > 0.50:
                    signal = "HOLD"
                else:
                    signal = "PASS"
                
                c['quantum_confidence'] = confidence * 100
                c['quantum_signal'] = signal
                c['quantum_expvals'] = [float(e) for e in expvals]
                
            except Exception as e:
                print(f"  Quantum error for {symbol}: {e}")
                c['quantum_confidence'] = 50.0
                c['quantum_signal'] = "HOLD"
        
        return top15
    
    def calculate_x_potential(self, coin: Dict) -> str:
        """Calculate potential x return"""
        mcap = coin['market_cap']
        
        if mcap < 5_000_000:
            return "50-100x"
        elif mcap < 20_000_000:
            return "20-50x"
        elif mcap < 100_000_000:
            return "10-20x"
        else:
            return "5-10x"
    
    def display_results(self, coins: List[Dict]):
        """Display final 20-100x picks"""
        print("\n" + "=" * 100)
        print("DEEP VALUE ALPHA - 20-100X POTENTIAL COINS")
        print("=" * 100)
        
        # Sort by quantum confidence
        ranked = sorted(coins, key=lambda x: x.get('quantum_confidence', 0), reverse=True)
        
        print("\n{:<4} {:<10} {:<20} {:<12} {:<12} {:<10} {:<10} {:<12} {:<12}".format(
            "#", "Symbol", "Name", "MCap", "Price", "Score", "Quantum", "Signal", "Potential"))
        print("-" * 100)
        
        for i, c in enumerate(ranked[:10], 1):
            mcap = c['market_cap'] / 1_000_000
            potential = self.calculate_x_potential(c)
            
            print("{:<4} {:<10} {:<20} ${:<11.2f}M ${:<11.6f} {:<10.1f} {:<10.1f}% {:<12} {:<12}".format(
                i, c['symbol'], c['name'][:18], mcap, c['price'],
                c['total_score'], c.get('quantum_confidence', 0), 
                c.get('quantum_signal', 'HOLD'), potential))
        
        print("\n" + "=" * 100)
        print("DETAILED ANALYSIS:")
        print("=" * 100)
        
        for i, c in enumerate(ranked[:10], 1):
            print(f"\n#{i} {c['symbol']} - {c['name']}")
            print(f"  Market Cap: ${c['market_cap']/1_000_000:.2f}M")
            print(f"  Price: ${c['price']:.6f}")
            print(f"  All-Time High: ${c.get('ath', 0):.6f} ({c.get('ath_change', 0):.1f}% from ATH)")
            print(f"  To ATH: {c.get('from_ath', 0):.1f}x from current price")
            print(f"  24h: {c['change_24h']:+.1f}% | 7d: {c['change_7d']:+.1f}%")
            print(f"  Volume/MCap: {c.get('vol_mcap_ratio', 0):.1f}%")
            print(f"  Total Score: {c['total_score']:.1f}/100")
            print(f"  Quantum: {c.get('quantum_signal', 'HOLD')} {c.get('quantum_confidence', 0):.1f}%")
            print(f"  20-100x Potential: {self.calculate_x_potential(c)}")
            
            if 'scores' in c:
                s = c['scores']
                print(f"  Breakdown: UnderVal={s['undervalued']:.0f} Size={s['size']:.0f} "
                      f"Recovery={s['recovery']:.0f} Activity={s['activity']:.0f}")
            
            # Why this is a deep value pick
            reasons = []
            ath_change = c.get('ath_change', 0)
            if -95 <= ath_change <= -70:
                reasons.append(f"Deeply undervalued ({ath_change:.0f}% from ATH)")
            if c['market_cap'] < 10_000_000:
                reasons.append("Micro-cap = massive upside potential")
            if c.get('from_ath', 0) > 50:
                reasons.append(f"{c.get('from_ath', 0):.0f}x to ATH = huge recovery")
            if c.get('vol_mcap_ratio', 0) > 20:
                reasons.append("High volume = real interest")
            if c['change_24h'] > 0 and c['change_7d'] > 0:
                reasons.append("Building momentum")
            elif c['change_24h'] < -5:
                reasons.append("Dip buy opportunity before run")
            
            print(f"\n  Why 20-100x potential:")
            for r in reasons:
                print(f"    - {r}")
            
            # Risk warning
            risks = []
            if c['vol_mcap_ratio'] < 5:
                risks.append("Low volume - hard to exit")
            if c['change_30d'] < -50:
                risks.append("Downtrend - may keep falling")
            if c['market_cap'] < 1_000_000:
                risks.append("Ultra micro-cap = high risk")
            
            if risks:
                print(f"  ⚠️  Risks:")
                for r in risks:
                    print(f"    - {r}")
    
    def save_results(self, coins: List[Dict]):
        """Save results"""
        import os
        os.makedirs(DATA_DIR, exist_ok=True)
        
        ranked = sorted(coins, key=lambda x: x.get('quantum_confidence', 0), reverse=True)
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'strategy': 'Deep Value 20-100x',
            'criteria': {
                'market_cap': '$1M-$500M',
                'undervaluation': 'Deep from ATH',
                'volume': 'Real activity',
                'potential': '20-100x returns'
            },
            'top_10': ranked[:10]
        }
        
        with open(f"{DATA_DIR}/deep_value_alpha.json", "w") as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\nSaved: {DATA_DIR}/deep_value_alpha.json")
    
    def run(self):
        """Full deep value pipeline"""
        print("\n" + "=" * 100)
        print("CORTEX DEEP VALUE ALPHA HUNTER")
        print("Finding 20-100x opportunities with real fundamentals")
        print("=" * 100)
        
        # Step 1: Fetch
        coins = self.fetch_coins()
        if not coins:
            print("No coins found!")
            return
        
        print(f"\nFound {len(coins)} candidates")
        
        # Step 2: Score
        coins = self.score_deep_value(coins)
        
        # Step 3: Filter
        coins = self.filter_high_potential(coins)
        
        # Step 4: Quantum
        coins = self.run_quantum_analysis(coins)
        
        # Step 5: Display
        self.display_results(coins)
        
        # Save
        self.save_results(coins)
        
        print("\n" + "=" * 100)
        print("DEEP VALUE HUNT COMPLETE")
        print("These are your highest conviction 20-100x plays")
        print("=" * 100)

def main():
    screener = DeepValueScreener()
    screener.run()

if __name__ == "__main__":
    main()
