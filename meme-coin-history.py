#!/usr/bin/env python3
"""
MEME COIN HISTORICAL DATA COLLECTOR
Fetches and stores historical data for all tracked meme coins
Uses CoinGecko API for historical prices, volumes, market caps
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time

class MemeCoinHistoryCollector:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.data_dir = 'meme_coin_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Top meme coins to track
        self.tracked_coins = {
            'bonk': 'BONK',
            'dogwifhat': 'WIF',
            'floki': 'FLOKI',
            'pepe': 'PEPE',
            'shiba-inu': 'SHIB',
            'dogecoin': 'DOGE',
            'arbitrum': 'ARB',
            'jupiter-exchange-solana': 'JUP',
            'fartcoin': 'FARTCOIN',
            'popcat': 'POPCAT',
            'mog-coin': 'MOG',
            'gigachad-2': 'GIGA',
            'apu-s-memecoin': 'APU',
            'billy': 'BILLY',
            'michicoin': 'MICHI',
            'retardio': 'RETARDIO',
            'zerebro': 'ZEREBRO',
            'ai16z': 'AI16Z',
            'fwog': 'FWOG',
            'pnut': 'PNUT'
        }
    
    def fetch_historical_data(self, coin_id, days=365):
        """Fetch historical market data for a coin"""
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Process data
            history = []
            prices = data.get('prices', [])
            market_caps = data.get('market_caps', [])
            volumes = data.get('total_volumes', [])
            
            for i in range(len(prices)):
                timestamp = prices[i][0]
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                
                history.append({
                    'date': date,
                    'timestamp': timestamp,
                    'price': prices[i][1],
                    'market_cap': market_caps[i][1] if i < len(market_caps) else 0,
                    'volume': volumes[i][1] if i < len(volumes) else 0
                })
            
            return history
            
        except Exception as e:
            print(f"Error fetching {coin_id}: {e}")
            return None
    
    def calculate_metrics(self, history):
        """Calculate comprehensive metrics from historical data"""
        if not history or len(history) < 2:
            return {}
        
        # Latest data
        latest = history[-1]
        
        # Price changes
        price_1d = history[-2]['price'] if len(history) >= 2 else latest['price']
        price_7d = history[-8]['price'] if len(history) >= 8 else latest['price']
        price_30d = history[-31]['price'] if len(history) >= 31 else latest['price']
        price_90d = history[-91]['price'] if len(history) >= 91 else latest['price']
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(history)):
            if history[i-1]['price'] > 0:
                ret = (history[i]['price'] - history[i-1]['price']) / history[i-1]['price']
                returns.append(ret)
        
        # Volatility (annualized)
        volatility = 0
        if returns:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            daily_vol = variance ** 0.5
            volatility = daily_vol * (365 ** 0.5)  # Annualized
        
        # Volume metrics
        recent_volume = [h['volume'] for h in history[-7:]]
        avg_volume_7d = sum(recent_volume) / len(recent_volume) if recent_volume else 0
        
        older_volume = [h['volume'] for h in history[-30:-7]]
        avg_volume_30d = sum(older_volume) / len(older_volume) if older_volume else 0
        
        # Price metrics
        prices = [h['price'] for h in history]
        max_price = max(prices) if prices else 0
        min_price = min(prices) if prices else 0
        
        # Moving averages
        ma_7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else latest['price']
        ma_30 = sum(prices[-30:]) / 30 if len(prices) >= 30 else latest['price']
        
        # Support and resistance (simplified)
        support = min(prices[-30:]) if len(prices) >= 30 else min_price
        resistance = max(prices[-30:]) if len(prices) >= 30 else max_price
        
        return {
            'current_price': latest['price'],
            'current_mcap': latest['market_cap'],
            'current_volume': latest['volume'],
            
            'price_change_1d': ((latest['price'] - price_1d) / price_1d * 100) if price_1d > 0 else 0,
            'price_change_7d': ((latest['price'] - price_7d) / price_7d * 100) if price_7d > 0 else 0,
            'price_change_30d': ((latest['price'] - price_30d) / price_30d * 100) if price_30d > 0 else 0,
            'price_change_90d': ((latest['price'] - price_90d) / price_90d * 100) if price_90d > 0 else 0,
            
            'volatility_annualized': volatility * 100,
            'avg_volume_7d': avg_volume_7d,
            'avg_volume_30d': avg_volume_30d,
            'volume_trend': 'UP' if avg_volume_7d > avg_volume_30d else 'DOWN',
            
            'max_price_30d': max(prices[-30:]) if len(prices) >= 30 else max_price,
            'min_price_30d': min(prices[-30:]) if len(prices) >= 30 else min_price,
            'support': support,
            'resistance': resistance,
            
            'ma_7': ma_7,
            'ma_30': ma_30,
            'trend': 'BULLISH' if ma_7 > ma_30 else 'BEARISH',
            
            'distance_from_ath': ((latest['price'] - max_price) / max_price * 100) if max_price > 0 else 0,
            'distance_from_support': ((latest['price'] - support) / support * 100) if support > 0 else 0,
            'distance_from_resistance': ((resistance - latest['price']) / latest['price'] * 100) if latest['price'] > 0 else 0,
            
            'data_points': len(history),
            'date_range': f"{history[0]['date']} to {history[-1]['date']}"
        }
    
    def save_data(self, coin_id, symbol, history, metrics):
        """Save historical data and metrics"""
        data = {
            'coin_id': coin_id,
            'symbol': symbol,
            'last_updated': datetime.now().isoformat(),
            'metrics': metrics,
            'history': history[-30:]  # Keep last 30 days for file size
        }
        
        filename = f"{symbol}_history.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        return filepath
    
    def collect_all(self, days=365):
        """Collect historical data for all tracked coins"""
        print("=" * 80)
        print("MEME COIN HISTORICAL DATA COLLECTOR")
        print(f"Collecting {days} days of data for {len(self.tracked_coins)} coins")
        print("=" * 80)
        print()
        
        results = []
        
        for coin_id, symbol in self.tracked_coins.items():
            print(f"Fetching {symbol}...", end=" ")
            
            history = self.fetch_historical_data(coin_id, days)
            
            if history:
                metrics = self.calculate_metrics(history)
                filepath = self.save_data(coin_id, symbol, history, metrics)
                
                print(f"OK - {len(history)} days | Price: ${metrics['current_price']:.6f} | MCap: ${metrics['current_mcap']:,.0f}")
                
                results.append({
                    'symbol': symbol,
                    'coin_id': coin_id,
                    'filepath': filepath,
                    'metrics': metrics
                })
            else:
                print("FAILED")
            
            # Rate limiting
            time.sleep(1.5)
        
        # Summary
        print("\n" + "=" * 80)
        print("COLLECTION COMPLETE")
        print("=" * 80)
        print(f"Successfully collected: {len(results)}/{len(self.tracked_coins)} coins")
        
        return results
    
    def load_historical_data(self, symbol):
        """Load previously saved historical data"""
        filepath = os.path.join(self.data_dir, f"{symbol}_history.json")
        
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {symbol}: {e}")
                return None
        
        return None
    
    def get_combined_metrics(self):
        """Get metrics for all tracked coins"""
        all_metrics = {}
        
        for coin_id, symbol in self.tracked_coins.items():
            data = self.load_historical_data(symbol)
            if data and 'metrics' in data:
                all_metrics[symbol] = data['metrics']
        
        return all_metrics


def main():
    collector = MemeCoinHistoryCollector()
    
    # Collect 365 days of historical data
    results = collector.collect_all(days=365)
    
    # Display summary
    print("\nHistorical Data Summary:")
    print("-" * 80)
    
    for r in results:
        m = r['metrics']
        print(f"{r['symbol']:12} | Price: ${m['current_price']:>12.6f} | "
              f"30d: {m['price_change_30d']:>7.1f}% | "
              f"Trend: {m['trend']:>8} | "
              f"Vol: {m['volatility_annualized']:>5.1f}%")


if __name__ == "__main__":
    main()
