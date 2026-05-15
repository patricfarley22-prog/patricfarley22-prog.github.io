#!/usr/bin/env python3
"""
MEME COIN QUANTUM ANALYZER WITH HISTORICAL DATA
Uses saved historical data + quantum AI for accurate signals
"""

import json
import os
import subprocess
from datetime import datetime

class QuantumHistoricalAnalyzer:
    def __init__(self):
        self.data_dir = 'meme_coin_data'
        
        # Load saved historical data
        self.historical_data = self.load_all_historical()
    
    def load_all_historical(self):
        """Load all saved historical data"""
        data = {}
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('_history.json'):
                symbol = filename.replace('_history.json', '')
                filepath = os.path.join(self.data_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        data[symbol] = json.load(f)
                except Exception as e:
                    print(f"Error loading {symbol}: {e}")
        
        return data
    
    def run_quantum(self, coin_data, historical):
        """Run quantum analysis with historical context"""
        metrics = historical.get('metrics', {})
        
        # Current data
        price_change = coin_data.get('price_change_24h', 0)
        volume = coin_data.get('total_volume', 0)
        mcap = coin_data.get('market_cap', 1)
        
        # Historical context (normalized)
        trend_score = 0.7 if metrics.get('trend') == 'BULLISH' else 0.3
        vol_score = min(metrics.get('volatility_annualized', 50) / 200, 1)
        momentum = metrics.get('price_change_7d', 0) / 100
        sentiment = 0.5 + (metrics.get('price_change_30d', 0) / 200)
        
        args = [
            str(price_change / 100),
            str(volume / 1_000_000),
            '0.5',
            str(momentum),
            str(sentiment),
            '0.55',
            '0.45',
            str(min(volume / mcap, 1)),
            '0.5',
            str(min(volume / 10_000_000, 1))
        ]
        
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'quantum_analyzer.py')
            result = subprocess.run(
                ['python', script_path] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                start = output.find('{')
                end = output.rfind('}')
                if start != -1 and end != -1:
                    return json.loads(output[start:end+1])
            
            return {'signal': 'ERROR', 'confidence': 0}
        except Exception as e:
            return {'signal': 'ERROR', 'confidence': 0}
    
    def analyze_saved_coins(self):
        """Analyze all coins with saved historical data"""
        print("=" * 80)
        print("QUANTUM MEME COIN ANALYZER WITH HISTORICAL DATA")
        print("=" * 80)
        print()
        
        results = []
        
        for symbol, data in self.historical_data.items():
            print(f"\nAnalyzing {symbol}...")
            print("-" * 60)
            
            metrics = data.get('metrics', {})
            history = data.get('history', [])
            
            # Display historical metrics
            print(f"Historical Data: {metrics.get('data_points', 0)} days")
            print(f"Price: ${metrics.get('current_price', 0):.8f}")
            print(f"Market Cap: ${metrics.get('current_mcap', 0):,.0f}")
            print(f"7D Change: {metrics.get('price_change_7d', 0):.2f}%")
            print(f"30D Change: {metrics.get('price_change_30d', 0):.2f}%")
            print(f"Trend: {metrics.get('trend', 'UNKNOWN')}")
            print(f"Volatility: {metrics.get('volatility_annualized', 0):.1f}%")
            print(f"Support: ${metrics.get('support', 0):.8f}")
            print(f"Resistance: ${metrics.get('resistance', 0):.8f}")
            
            # Create coin data for quantum
            coin_data = {
                'price_change_24h': metrics.get('price_change_1d', 0),
                'total_volume': metrics.get('current_volume', 0),
                'market_cap': metrics.get('current_mcap', 1)
            }
            
            # Run quantum
            quantum = self.run_quantum(coin_data, data)
            
            signal = quantum.get('signal', 'UNKNOWN')
            confidence = quantum.get('confidence', 0)
            entanglement = quantum.get('entanglement_strength', 0)
            
            print(f"\nQuantum Signal: {signal}")
            print(f"Confidence: {confidence*100:.1f}%")
            print(f"Entanglement: {entanglement:.3f}")
            
            results.append({
                'symbol': symbol,
                'metrics': metrics,
                'quantum': quantum
            })
        
        # Rank by confidence
        results.sort(key=lambda x: x['quantum'].get('confidence', 0), reverse=True)
        
        print("\n" + "=" * 80)
        print("RANKED BY QUANTUM CONFIDENCE")
        print("=" * 80)
        print()
        
        print(f"{'#':<4} {'Symbol':<8} {'Signal':<10} {'Conf':<8} {'Price':<12} {'30d':<8} {'Trend':<8}")
        print("-" * 80)
        
        for i, r in enumerate(results, 1):
            q = r['quantum']
            m = r['metrics']
            
            print(f"{i:<4} {r['symbol']:<8} {q.get('signal','UNK'):<10} "
                  f"{q.get('confidence',0)*100:>6.1f}%  "
                  f"${m.get('current_price',0):<10.8f} "
                  f"{m.get('price_change_30d',0):>6.1f}%  "
                  f"{m.get('trend','UNK'):<8}")
        
        return results
    
    def save_analysis(self, results):
        """Save analysis results"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'coins_analyzed': len(results),
            'results': results
        }
        
        filepath = os.path.join(self.data_dir, 'quantum-historical-analysis.json')
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\nAnalysis saved to {filepath}")


def main():
    analyzer = QuantumHistoricalAnalyzer()
    results = analyzer.analyze_saved_coins()
    analyzer.save_analysis(results)
    
    print("\n" + "=" * 80)
    print(f"Analysis complete for {len(results)} coins with historical data")
    print("=" * 80)


if __name__ == "__main__":
    main()
