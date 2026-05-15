#!/usr/bin/env python3
"""
MEME COIN ANALYZER WITH QUANTUM AI + HISTORICAL DATA
Combines CoinGecko, historical data, and quantum analysis
"""

import requests
import json
import subprocess
import os
from datetime import datetime
import time

class FullMemeCoinAnalyzer:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.data_dir = 'meme_coin_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # CoinGecko IDs to symbols
        self.tracked_coins = {
            'bonk': 'BONK',
            'floki': 'FLOKI',
            'pepe': 'PEPE',
            'shiba-inu': 'SHIB',
            'dogecoin': 'DOGE',
            'arbitrum': 'ARB',
            'fartcoin': 'FARTCOIN'
        }
    
    def fetch_current_data(self, coin_id):
        """Fetch current market data"""
        url = f"{self.base_url}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            market = data.get('market_data', {})
            
            return {
                'id': coin_id,
                'symbol': data.get('symbol', '').upper(),
                'name': data.get('name'),
                'current_price': market.get('current_price', {}).get('usd', 0),
                'market_cap': market.get('market_cap', {}).get('usd', 0),
                'total_volume': market.get('total_volume', {}).get('usd', 0),
                'price_change_24h': market.get('price_change_percentage_24h', 0),
                'price_change_7d': market.get('price_change_percentage_7d', 0),
                'price_change_30d': market.get('price_change_percentage_30d', 0),
                'ath': market.get('ath', {}).get('usd', 0),
                'ath_change_percentage': market.get('ath_change_percentage', {}).get('usd', 0),
                'circulating_supply': market.get('circulating_supply', 0),
                'total_supply': market.get('total_supply', 0),
                'last_updated': market.get('last_updated')
            }
        except Exception as e:
            print(f"Error fetching {coin_id}: {e}")
            return None
    
    def fetch_historical_data(self, coin_id, days=90):
        """Fetch historical data with rate limiting"""
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            market_caps = data.get('market_caps', [])
            
            history = []
            for i in range(len(prices)):
                history.append({
                    'date': datetime.fromtimestamp(prices[i][0] / 1000).strftime('%Y-%m-%d'),
                    'price': prices[i][1],
                    'volume': volumes[i][1] if i < len(volumes) else 0,
                    'market_cap': market_caps[i][1] if i < len(market_caps) else 0
                })
            
            return history
        except Exception as e:
            print(f"Error fetching history for {coin_id}: {e}")
            return None
    
    def calculate_historical_metrics(self, history):
        """Calculate metrics from historical data"""
        if not history or len(history) < 2:
            return {}
        
        latest = history[-1]
        prices = [h['price'] for h in history]
        volumes = [h['volume'] for h in history]
        
        # Price changes
        price_7d = history[-8]['price'] if len(history) >= 8 else latest['price']
        price_30d = history[-31]['price'] if len(history) >= 31 else latest['price']
        
        # Moving averages
        ma_7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else latest['price']
        ma_30 = sum(prices[-30:]) / 30 if len(prices) >= 30 else latest['price']
        
        # Volatility
        returns = []
        for i in range(1, min(30, len(history))):
            if history[i-1]['price'] > 0:
                ret = (history[i]['price'] - history[i-1]['price']) / history[i-1]['price']
                returns.append(ret)
        
        volatility = 0
        if returns:
            mean = sum(returns) / len(returns)
            variance = sum((r - mean) ** 2 for r in returns) / len(returns)
            volatility = (variance ** 0.5) * 100
        
        return {
            'current_price': latest['price'],
            'current_volume': latest['volume'],
            'current_mcap': latest['market_cap'],
            'price_change_7d': ((latest['price'] - price_7d) / price_7d * 100) if price_7d > 0 else 0,
            'price_change_30d': ((latest['price'] - price_30d) / price_30d * 100) if price_30d > 0 else 0,
            'ma_7': ma_7,
            'ma_30': ma_30,
            'trend': 'BULLISH' if ma_7 > ma_30 else 'BEARISH',
            'volatility_30d': volatility,
            'avg_volume_7d': sum(volumes[-7:]) / 7 if len(volumes) >= 7 else latest['volume'],
            'support': min(prices[-30:]) if len(prices) >= 30 else min(prices),
            'resistance': max(prices[-30:]) if len(prices) >= 30 else max(prices),
            'max_price_30d': max(prices[-30:]) if len(prices) >= 30 else max(prices),
            'min_price_30d': min(prices[-30:]) if len(prices) >= 30 else min(prices),
        }
    
    def run_quantum_analysis(self, coin_data, historical_metrics):
        """Run quantum analyzer with historical context"""
        
        # Prepare features with historical context
        price_change = coin_data.get('price_change_24h', 0)
        volume = coin_data.get('total_volume', 0)
        mcap = coin_data.get('market_cap', 1)
        
        # Historical context
        trend_score = 0.7 if historical_metrics.get('trend') == 'BULLISH' else 0.3
        vol_score = min(historical_metrics.get('volatility_30d', 50) / 100, 1)
        momentum = historical_metrics.get('price_change_7d', 0) / 100
        
        args = [
            str(price_change / 100),
            str(volume / 1_000_000),
            '0.5',
            str(momentum),
            str(trend_score),
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
    
    def analyze_coin(self, coin_id, symbol):
        """Full analysis of a single coin"""
        print(f"\nAnalyzing {symbol}...")
        print("-" * 60)
        
        # Fetch current data
        current = self.fetch_current_data(coin_id)
        if not current:
            return None
        
        print(f"Current: ${current['current_price']:.6f} | "
              f"MCap: ${current['market_cap']:,.0f} | "
              f"24h: {current['price_change_24h']:.2f}%")
        
        # Fetch historical data
        history = self.fetch_historical_data(coin_id, days=90)
        time.sleep(2)  # Rate limiting
        
        if history:
            metrics = self.calculate_historical_metrics(history)
            
            print(f"History: {len(history)} days | "
                  f"Trend: {metrics['trend']} | "
                  f"Vol: {metrics['volatility_30d']:.1f}% | "
                  f"7d: {metrics['price_change_7d']:.2f}%")
            
            # Quantum analysis with historical context
            quantum = self.run_quantum_analysis(current, metrics)
            
            signal = quantum.get('signal', 'UNKNOWN')
            confidence = quantum.get('confidence', 0)
            entanglement = quantum.get('entanglement_strength', 0)
            
            print(f"Quantum: {signal} ({confidence*100:.1f}%) | Entanglement: {entanglement:.3f}")
            
            return {
                'symbol': symbol,
                'coin_id': coin_id,
                'current': current,
                'historical_metrics': metrics,
                'quantum': quantum,
                'history': history[-30:]  # Keep last 30 days
            }
        
        return None
    
    def analyze_all(self):
        """Analyze all tracked coins"""
        print("=" * 80)
        print("MEME COIN ANALYZER WITH QUANTUM + HISTORICAL DATA")
        print("=" * 80)
        
        results = []
        
        for coin_id, symbol in self.tracked_coins.items():
            result = self.analyze_coin(coin_id, symbol)
            if result:
                results.append(result)
            
            time.sleep(3)  # Rate limiting between coins
        
        # Save results
        self.save_results(results)
        
        # Display summary
        self.display_summary(results)
        
        return results
    
    def save_results(self, results):
        """Save analysis results"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'coins_analyzed': len(results),
            'results': results
        }
        
        filepath = os.path.join(self.data_dir, 'full-analysis.json')
        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\nResults saved to {filepath}")
    
    def display_summary(self, results):
        """Display summary of all coins"""
        print("\n" + "=" * 80)
        print("SUMMARY - RANKED BY QUANTUM CONFIDENCE")
        print("=" * 80)
        
        # Sort by confidence
        sorted_results = sorted(results, 
                              key=lambda x: x['quantum'].get('confidence', 0), 
                              reverse=True)
        
        print(f"\n{'#':<4} {'Symbol':<8} {'Signal':<10} {'Conf':<8} {'Price':<12} {'24h':<8} {'Trend':<8}")
        print("-" * 80)
        
        for i, r in enumerate(sorted_results, 1):
            q = r['quantum']
            c = r['current']
            h = r['historical_metrics']
            
            print(f"{i:<4} {r['symbol']:<8} {q.get('signal','UNK'):<10} "
                  f"{q.get('confidence',0)*100:>6.1f}%  "
                  f"${c['current_price']:<10.6f} "
                  f"{c['price_change_24h']:>6.1f}%  "
                  f"{h.get('trend','UNK'):<8}")


def main():
    analyzer = FullMemeCoinAnalyzer()
    results = analyzer.analyze_all()
    
    print("\n" + "=" * 80)
    print(f"Analysis complete for {len(results)} coins")
    print("=" * 80)


if __name__ == "__main__":
    main()
