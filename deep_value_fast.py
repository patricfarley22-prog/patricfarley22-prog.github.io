#!/usr/bin/env python3
"""
CORTEX DEEP VALUE ALPHA - FAST VERSION
Using known high-potential coins for immediate 20-100x analysis
"""

import json
import math
from datetime import datetime
from typing import Dict, List

# Quantum
import pennylane as qml
from pennylane import numpy as np

DATA_DIR = "meme_coin_data"

class DeepValueFast:
    """Fast deep value screener using known data"""
    
    def __init__(self):
        self.dev = qml.device("default.qubit", wires=4, shots=1000)
    
    def run_quantum(self, features):
        """Quantum circuit"""
        @qml.qnode(self.dev)
        def circuit(f):
            for i, val in enumerate(f[:4]):
                qml.RY(val * np.pi, wires=i)
            
            qml.CNOT(wires=[0, 1])
            qml.CNOT(wires=[1, 2])
            qml.CNOT(wires=[2, 3])
            qml.CNOT(wires=[0, 3])
            
            for i in range(4):
                qml.RX(f[i % len(f)] * np.pi, wires=i)
                qml.RZ(f[(i+2) % len(f)] * np.pi, wires=i)
            
            return [qml.expval(qml.PauliZ(i)) for i in range(4)]
        
        return circuit(features)
    
    def analyze(self):
        """Analyze known high-potential coins"""
        
        # High-potential coins from our tracking + research
        COINS = [
            {"symbol": "HACHI", "name": "Hachi", "market_cap": 22000, "price": 0.000022, 
             "ath": 0.0005, "ath_change": -95.6, "change_24h": -2.90, "change_7d": -5.0,
             "volume_24h": 500, "total_supply": 1000000000},
            
            {"symbol": "PENGO", "name": "Pengo", "market_cap": 590000, "price": 0.000592,
             "ath": 0.005, "ath_change": -88.2, "change_24h": -2.38, "change_7d": -5.0,
             "volume_24h": 12000, "total_supply": 1000000000},
            
            {"symbol": "OMEGAX", "name": "OmegaX", "market_cap": 360000, "price": 0.000365,
             "ath": 0.003, "ath_change": -87.8, "change_24h": -1.73, "change_7d": 0.0,
             "volume_24h": 3000, "total_supply": 1000000000},
            
            {"symbol": "BITTY", "name": "The Bitcoin Mascot", "market_cap": 933910, "price": 0.00092,
             "ath": 0.01, "ath_change": -90.8, "change_24h": -2.03, "change_7d": 0.0,
             "volume_24h": 19556, "total_supply": 1000000000},
            
            {"symbol": "WOBBLES", "name": "Wobbles", "market_cap": 910000, "price": 0.000914,
             "ath": 0.008, "ath_change": -88.6, "change_24h": -19.49, "change_7d": -25.0,
             "volume_24h": 90000, "total_supply": 1000000000},
            
            {"symbol": "TOKABU", "name": "Tokabu", "market_cap": 2410000, "price": 0.00241,
             "ath": 0.02, "ath_change": -87.9, "change_24h": -15.49, "change_7d": -20.0,
             "volume_24h": 153000, "total_supply": 1000000000},
            
            {"symbol": "DOWGE", "name": "Dowge", "market_cap": 3200000, "price": 0.00321,
             "ath": 0.025, "ath_change": -87.2, "change_24h": -5.34, "change_7d": -8.0,
             "volume_24h": 22000, "total_supply": 1000000000},
            
            {"symbol": "House", "name": "Housecoin", "market_cap": 3338250, "price": 0.00335,
             "ath": 0.015, "ath_change": -77.7, "change_24h": -14.57, "change_7d": 0.0,
             "volume_24h": 92872, "total_supply": 1000000000},
            
            {"symbol": "ZEREBRO", "name": "zerebro", "market_cap": 28471555, "price": 0.02821,
             "ath": 0.15, "ath_change": -81.2, "change_24h": -2.0, "change_7d": 0.0,
             "volume_24h": 2990806, "total_supply": 1000000000},
            
            {"symbol": "GIGA", "name": "Gigachad", "market_cap": 42870000, "price": 0.00447,
             "ath": 0.012, "ath_change": -62.8, "change_24h": -7.7, "change_7d": 0.0,
             "volume_24h": 1414240, "total_supply": 1000000000},
            
            {"symbol": "CGPT", "name": "ChainGPT", "market_cap": 39710000, "price": 0.04297,
             "ath": 0.5, "ath_change": -91.4, "change_24h": 16.1, "change_7d": 0.0,
             "volume_24h": 38000000, "total_supply": 1000000000},
            
            {"symbol": "UP", "name": "Superform", "market_cap": 28460000, "price": 0.148,
             "ath": 2.0, "ath_change": -92.6, "change_24h": -12.8, "change_7d": 0.0,
             "volume_24h": 21500000, "total_supply": 100000000},
            
            {"symbol": "DOGS", "name": "Dogs", "market_cap": 29930000, "price": 0.000058,
             "ath": 0.001, "ath_change": -94.2, "change_24h": -5.5, "change_7d": 0.0,
             "volume_24h": 19000000, "total_supply": 1000000000},
            
            {"symbol": "DEGEN", "name": "Degen", "market_cap": 35040000, "price": 0.00094,
             "ath": 0.02, "ath_change": -95.3, "change_24h": -10.6, "change_7d": 0.0,
             "volume_24h": 28600000, "total_supply": 1000000000},
            
            {"symbol": "TROLL", "name": "Troll", "market_cap": 116950000, "price": 0.1165,
             "ath": 0.85, "ath_change": -86.3, "change_24h": -11.5, "change_7d": -20.0,
             "volume_24h": 13400000, "total_supply": 1000000000}
        ]
        
        # Calculate metrics
        for c in COINS:
            # From ATH multiple
            if c['ath'] > 0 and c['price'] > 0:
                c['from_ath'] = c['ath'] / c['price']
            else:
                c['from_ath'] = 0
            
            # Volume/mcap ratio
            if c['market_cap'] > 0:
                c['vol_ratio'] = (c['volume_24h'] / c['market_cap']) * 100
            else:
                c['vol_ratio'] = 0
            
            # Deep value score
            scores = {}
            
            # Undervaluation (0-100)
            ath_change = c['ath_change']
            if -95 <= ath_change <= -85:
                scores['undervalued'] = 95
            elif -85 < ath_change <= -70:
                scores['undervalued'] = 85
            elif -70 < ath_change <= -50:
                scores['undervalued'] = 70
            else:
                scores['undervalued'] = 50
            
            # Size (smaller = more upside)
            mcap = c['market_cap']
            if mcap < 1_000_000:
                scores['size'] = 100
            elif mcap < 5_000_000:
                scores['size'] = 90
            elif mcap < 20_000_000:
                scores['size'] = 80
            elif mcap < 100_000_000:
                scores['size'] = 65
            else:
                scores['size'] = 50
            
            # Recovery potential
            from_ath = c['from_ath']
            if from_ath >= 100:
                scores['recovery'] = 100
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
            
            # Activity
            vol_ratio = c['vol_ratio']
            if vol_ratio > 50:
                scores['activity'] = 100
            elif vol_ratio > 20:
                scores['activity'] = 80
            elif vol_ratio > 10:
                scores['activity'] = 60
            else:
                scores['activity'] = 40
            
            # Momentum
            chg_24h = c['change_24h']
            if 5 < chg_24h < 30:
                scores['momentum'] = 90
            elif 0 < chg_24h < 5:
                scores['momentum'] = 70
            elif -15 < chg_24h < 0:
                scores['momentum'] = 75  # Dip buy
            else:
                scores['momentum'] = 50
            
            # Total score
            weights = {
                'undervalued': 0.30,
                'size': 0.25,
                'recovery': 0.25,
                'activity': 0.10,
                'momentum': 0.10
            }
            
            total = sum(scores[k] * weights[k] for k in weights)
            c['scores'] = scores
            c['total_score'] = total
        
        # Run quantum on top 10
        top10 = sorted(COINS, key=lambda x: x['total_score'], reverse=True)[:10]
        
        for c in top10:
            f1 = min(1.0, c['scores']['undervalued'] / 100)
            f2 = min(1.0, c['scores']['size'] / 100)
            f3 = min(1.0, c['scores']['recovery'] / 100)
            f4 = min(1.0, c['scores']['activity'] / 100)
            
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
                print(f"Quantum error: {e}")
                c['quantum_confidence'] = 50.0
                c['quantum_signal'] = "HOLD"
        
        return top10
    
    def calculate_potential(self, coin) -> str:
        mcap = coin['market_cap']
        from_ath = coin.get('from_ath', 0)
        
        if from_ath > 50:
            return "50-100x"
        elif from_ath > 20:
            return "20-50x"
        elif from_ath > 10:
            return "10-20x"
        elif from_ath > 5:
            return "5-10x"
        else:
            return "2-5x"
    
    def display(self, coins):
        print("\n" + "=" * 100)
        print("CORTEX DEEP VALUE ALPHA - 20-100X POTENTIAL COINS")
        print("=" * 100)
        print("\nScoring: Undervaluation(30%) + Size(25%) + Recovery(25%) + Activity(10%) + Momentum(10%)")
        
        # Sort by quantum confidence
        ranked = sorted(coins, key=lambda x: x.get('quantum_confidence', 0), reverse=True)
        
        print("\n{:<4} {:<10} {:<20} {:<12} {:<10} {:<10} {:<12} {:<12} {:<12}".format(
            "#", "Symbol", "Name", "MCap", "From ATH", "Score", "Quantum", "Signal", "Potential"))
        print("-" * 100)
        
        for i, c in enumerate(ranked, 1):
            mcap = c['market_cap'] / 1_000_000
            from_ath = c.get('from_ath', 0)
            potential = self.calculate_potential(c)
            
            print("{:<4} {:<10} {:<20} ${:<11.3f}M {:<10.1f}x {:<10.1f} {:<12.1f}% {:<12} {:<12}".format(
                i, c['symbol'], c['name'][:18], mcap, from_ath,
                c['total_score'], c.get('quantum_confidence', 0),
                c.get('quantum_signal', 'HOLD'), potential))
        
        print("\n" + "=" * 100)
        print("TOP 5 DEEP VALUE PICKS WITH REASONING:")
        print("=" * 100)
        
        for i, c in enumerate(ranked[:5], 1):
            print(f"\n{'='*100}")
            print(f"#{i} {c['symbol']} - {c['name']} - {c.get('quantum_signal', 'HOLD')}")
            print(f"{'='*100}")
            
            mcap = c['market_cap']
            print(f"\n  MARKET DATA:")
            print(f"    Market Cap: ${mcap/1_000_000:.3f}M")
            print(f"    Price: ${c['price']:.6f}")
            print(f"    All-Time High: ${c['ath']:.6f}")
            print(f"    From ATH: {c['from_ath']:.1f}x (current price to ATH)")
            print(f"    ATH Drop: {c['ath_change']:.1f}%")
            print(f"    24h: {c['change_24h']:+.1f}% | 7d: {c['change_7d']:+.1f}%")
            print(f"    Volume/MCap: {c.get('vol_ratio', 0):.1f}%")
            
            print(f"\n  SCORES:")
            s = c['scores']
            print(f"    Total: {c['total_score']:.1f}/100")
            print(f"    Undervalued: {s['undervalued']}/100")
            print(f"    Size: {s['size']}/100")
            print(f"    Recovery: {s['recovery']}/100")
            print(f"    Activity: {s['activity']}/100")
            print(f"    Momentum: {s['momentum']}/100")
            
            print(f"\n  QUANTUM ANALYSIS:")
            print(f"    Confidence: {c.get('quantum_confidence', 0):.1f}%")
            print(f"    Signal: {c.get('quantum_signal', 'HOLD')}")
            if 'quantum_expvals' in c:
                print(f"    Measurements: {[f'{e:.3f}' for e in c['quantum_expvals']]}")
            
            print(f"\n  20-100X POTENTIAL: {self.calculate_potential(c)}")
            
            print(f"\n  WHY THIS IS A DEEP VALUE PLAY:")
            reasons = []
            if c['ath_change'] < -85:
                reasons.append(f"EXTREMELY undervalued ({c['ath_change']:.0f}% from ATH)")
            elif c['ath_change'] < -70:
                reasons.append(f"Deeply undervalued ({c['ath_change']:.0f}% from ATH)")
            
            if c['market_cap'] < 1_000_000:
                reasons.append("Micro-cap under $1M = massive upside if it catches traction")
            elif c['market_cap'] < 5_000_000:
                reasons.append("Small cap under $5M = huge room to grow")
            
            if c['from_ath'] > 50:
                reasons.append(f"{c['from_ath']:.0f}x to ATH = even recovering 10% gets you 5x")
            elif c['from_ath'] > 20:
                reasons.append(f"{c['from_ath']:.0f}x to ATH = recovering 20% gets you 4x")
            elif c['from_ath'] > 10:
                reasons.append(f"{c['from_ath']:.0f}x to ATH = recovering 30% gets you 3x")
            
            if c.get('vol_ratio', 0) > 20:
                reasons.append("High volume = real traders are interested")
            
            if c['change_24h'] < -10:
                reasons.append(f"Dipped {c['change_24h']:.0f}% = perfect entry before recovery")
            elif c['change_24h'] > 5:
                reasons.append(f"Already moving +{c['change_24h']:.0f}% = momentum building")
            
            for r in reasons:
                print(f"    - {r}")
            
            print(f"\n  HOLD STRATEGY:")
            print(f"    - Entry: Current price ${c['price']:.6f}")
            print(f"    - Target 1: ${c['ath'] * 0.2:.6f} (20% of ATH = {c['from_ath'] * 0.2:.1f}x)")
            print(f"    - Target 2: ${c['ath'] * 0.5:.6f} (50% of ATH = {c['from_ath'] * 0.5:.1f}x)")
            print(f"    - Target 3: ${c['ath']:.6f} (Full ATH = {c['from_ath']:.1f}x)")
            print(f"    - Stop Loss: ${c['price'] * 0.5:.6f} (-50% max pain)")
            print(f"    - Timeframe: 3-12 months (patience required)")
            
            risks = []
            if c['vol_ratio'] < 5:
                risks.append("Low volume - may be hard to sell")
            if c['change_7d'] < -20:
                risks.append("Downtrend - could keep falling")
            if c['market_cap'] < 500_000:
                risks.append("Ultra micro-cap = very high risk")
            
            if risks:
                print(f"\n  [WARN] RISKS:")
                for r in risks:
                    print(f"    - {r}")
            else:
                print(f"\n  [OK] Lower risk profile")
        
        # Save
        import os
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(f"{DATA_DIR}/deep_value_alpha.json", "w") as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'strategy': 'Deep Value 20-100x',
                'top_5': ranked[:5]
            }, f, indent=2, default=str)
        
        print(f"\n{'='*100}")
        print(f"Saved: {DATA_DIR}/deep_value_alpha.json")
        print(f"{'='*100}")

def main():
    print("\n" + "=" * 100)
    print("CORTEX DEEP VALUE ALPHA HUNTER")
    print("Finding 20-100x opportunities for long-term holds")
    print("=" * 100)
    
    screener = DeepValueFast()
    coins = screener.analyze()
    screener.display(coins)
    
    print("\n" + "=" * 100)
    print("DEEP VALUE HUNT COMPLETE")
    print("These are your highest conviction long-term plays")
    print("Patience + conviction = 20-100x potential")
    print("=" * 100)

if __name__ == "__main__":
    main()
