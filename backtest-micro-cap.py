#!/usr/bin/env python3
"""
MICRO-CAP BACKTESTER WITH STOP LOSSES
Backtests quantum signals on sub-$100M meme coins
"""

import json
import os
import requests
from datetime import datetime

class MicroCapBacktester:
    def __init__(self, initial_capital=1000):
        """Lower capital for micro-caps"""
        self.initial_capital = initial_capital
        self.data_dir = 'meme_coin_data'
    
    def generate_synthetic_history(self, symbol, ca, days=60):
        """Generate synthetic price history for micro-caps"""
        # Fetch current data
        try:
            response = requests.get(f'https://api.dexscreener.com/latest/dex/tokens/{ca}', timeout=10)
            data = response.json()
            pair = data.get('pairs', [{}])[0]
            
            current_price = float(pair.get('priceUsd', 0))
            change_24h = float(pair.get('priceChange', {}).get('h24', 0))
            change_7d = float(pair.get('priceChange', {}).get('h6', 0)) * 4  # Approximate
            volume_24h = float(pair.get('volume', {}).get('h24', 0))
            
            if current_price <= 0:
                return None
            
            # Generate realistic history
            import random
            random.seed(42)  # Reproducible
            
            history = []
            price = current_price
            
            # Work backwards from current price
            for i in range(days):
                # Create volatile micro-cap price action
                # Random walk with momentum and mean reversion
                trend = -change_24h / 30  # Revert to mean
                volatility = 0.08  # Micro-caps: 8% daily vol
                
                # Add momentum clusters (3-5 day trends)
                if i > 0 and i % 5 == 0:
                    trend += random.choice([-1, 1]) * 0.03
                
                daily_change = random.gauss(trend, volatility)
                
                # Occasional big moves (pumps/dumps)
                if random.random() < 0.1:  # 10% chance
                    daily_change += random.choice([-1, 1]) * random.uniform(0.15, 0.35)
                
                price = price * (1 + daily_change)
                price = max(price, current_price * 0.05)  # Floor at 5% of current
                
                # Synthetic volume (spikes on big moves)
                vol_mult = 3.0 if abs(daily_change) > 0.15 else 1.0
                vol = volume_24h * random.uniform(0.3, vol_mult)
                
                history.append({
                    'date': (datetime.now().replace(hour=0, minute=0, second=0)).isoformat(),
                    'price': price,
                    'volume': vol,
                    'market_cap': price * 1_000_000_000
                })
            
            # Reverse so oldest first
            history.reverse()
            
            # Update dates properly
            for i, h in enumerate(history):
                from datetime import timedelta
                h['date'] = (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d')
            
            return {
                'symbol': symbol,
                'history': history,
                'current_price': current_price,
                'source': 'synthetic'
            }
        except Exception as e:
            print(f"  Error generating history: {e}")
            return None
    
    def generate_signal(self, history, index):
        """Generate quantum-like signal for micro-caps"""
        if index < 14:
            return 'HOLD', 0.25
        
        current = history[index]
        price = current['price']
        
        # Calculate returns
        price_1d = history[index-1]['price']
        price_3d = history[index-3]['price']
        price_7d = history[index-7]['price']
        price_14d = history[index-14]['price']
        
        ret_1d = ((price - price_1d) / price_1d * 100) if price_1d > 0 else 0
        ret_3d = ((price - price_3d) / price_3d * 100) if price_3d > 0 else 0
        ret_7d = ((price - price_7d) / price_7d * 100) if price_7d > 0 else 0
        ret_14d = ((price - price_14d) / price_14d * 100) if price_14d > 0 else 0
        
        # Volume
        vol_now = current['volume']
        vol_avg = sum(h['volume'] for h in history[max(0,index-7):index]) / 7
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1
        
        signal = 'HOLD'
        confidence = 0.25
        
        # Micro-cap specific signals (more volatile, lower thresholds)
        # Oversold bounce (buy the dip)
        if ret_14d < -20 and ret_7d > -3:
            signal = 'BUY'
            confidence = 0.30 + abs(ret_14d) / 100
        # Momentum up
        elif ret_7d > 8 and ret_1d > 0 and vol_ratio > 1.2:
            signal = 'BUY'
            confidence = 0.35 + ret_7d / 100
        # Overbought
        elif ret_14d > 40 and ret_7d < 3:
            signal = 'SELL'
            confidence = 0.30 + abs(ret_14d) / 100
        # Momentum down
        elif ret_7d < -8 and ret_1d < 0 and vol_ratio > 1.2:
            signal = 'SELL'
            confidence = 0.35 + abs(ret_7d) / 100
        # Breakout
        elif abs(ret_1d) > 5 and vol_ratio > 1.5:
            signal = 'BUY' if ret_1d > 0 else 'SELL'
            confidence = 0.30 + abs(ret_1d) / 50
        # Volume spike without price move
        elif vol_ratio > 2.5 and abs(ret_1d) < 2:
            signal = 'BUY' if ret_7d < 0 else 'SELL'
            confidence = 0.30
        
        confidence = min(0.6, confidence)
        return signal, confidence
    
    def backtest(self, symbol, ca, threshold=0.30, position_size=0.25, stop_loss=-0.15):
        """Backtest with wider stops for micro-caps (15% vs 8% for majors)"""
        data = self.generate_synthetic_history(symbol, ca)
        if not data:
            return None
        
        history = data['history']
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity = [capital]
        stop_hits = 0
        
        for i in range(14, len(history)):
            signal, confidence = self.generate_signal(history, i)
            price = history[i]['price']
            
            # Check stop loss
            if position > 0 and entry_price > 0:
                pnl_pct = (price - entry_price) / entry_price
                if pnl_pct <= stop_loss:
                    sell_val = position * price
                    pnl = sell_val - trades[-1]['value']
                    pnl_pct_real = (pnl / trades[-1]['value']) * 100
                    capital += sell_val
                    
                    trades.append({
                        'type': 'STOP',
                        'price': price,
                        'pnl_pct': pnl_pct_real,
                        'day': i
                    })
                    stop_hits += 1
                    position = 0
                    entry_price = 0
                    continue
            
            # Execute trade
            if confidence >= threshold:
                if signal == 'BUY' and position == 0:
                    invest = capital * position_size
                    shares = invest / price
                    position = shares
                    entry_price = price
                    capital -= invest
                    trades.append({'type': 'BUY', 'price': price, 'value': invest, 'conf': confidence})
                
                elif signal == 'SELL' and position > 0:
                    sell_val = position * price
                    pnl = sell_val - trades[-1]['value']
                    pnl_pct = (pnl / trades[-1]['value']) * 100
                    capital += sell_val
                    trades.append({'type': 'SELL', 'price': price, 'pnl_pct': pnl_pct})
                    position = 0
                    entry_price = 0
            
            equity.append(capital + (position * price))
        
        # Close at end
        if position > 0:
            final_price = history[-1]['price']
            capital += position * final_price
        
        final = capital
        ret = ((final - self.initial_capital) / self.initial_capital) * 100
        
        completed = [t for t in trades if t['type'] in ['SELL', 'STOP']]
        wins = [t for t in completed if t.get('pnl_pct', 0) > 0]
        
        peak = equity[0]
        max_dd = 0
        for v in equity:
            if v > peak: peak = v
            dd = (peak - v) / peak
            if dd > max_dd: max_dd = dd
        
        return {
            'symbol': symbol,
            'return': ret,
            'trades': len(completed),
            'wins': len(wins),
            'stops': stop_hits,
            'win_rate': (len(wins) / len(completed) * 100) if completed else 0,
            'max_dd': max_dd * 100,
            'final_capital': final
        }
    
    def run_all(self, coins):
        """Backtest all micro-cap coins"""
        print("=" * 80)
        print("MICRO-CAP BACKTESTER WITH STOP LOSSES")
        print(f"Capital: ${self.initial_capital} | Stop Loss: 15% | Position: 25%")
        print("=" * 80)
        
        results = []
        for symbol, info in coins.items():
            if info.get('ca'):
                print(f"\nBacktesting {symbol}...")
                r = self.backtest(symbol, info['ca'])
                if r:
                    results.append(r)
                    status = "PROFIT" if r['return'] > 0 else "LOSS"
                    print(f"  {status}: {r['return']:+.2f}% | Trades: {r['trades']} (W:{r['wins']} S:{r['stops']})")
                    print(f"  Win Rate: {r['win_rate']:.1f}% | Max DD: {r['max_dd']:.2f}%")
                    print(f"  Final: ${r['final_capital']:.2f}")
        
        if results:
            avg_ret = sum(r['return'] for r in results) / len(results)
            print(f"\n{'='*80}")
            print("PORTFOLIO SUMMARY")
            print(f"{'='*80}")
            print(f"Average Return: {avg_ret:+.2f}%")
            print(f"Total Trades: {sum(r['trades'] for r in results)}")
            print(f"Total Stops Hit: {sum(r['stops'] for r in results)}")
            
            ranked = sorted(results, key=lambda x: x['return'], reverse=True)
            print(f"\nRanked:")
            for i, r in enumerate(ranked, 1):
                print(f"{i}. {r['symbol']}: {r['return']:+.2f}% ({r['trades']} trades)")
        
        return results


def main():
    bt = MicroCapBacktester(initial_capital=1000)
    
    coins = {
        'DOWGE': {'ca': 'DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump'},
        'WOBBLES': {'ca': '9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump'},
        'PENGO': {'ca': 'F2k82EcxLtzekq1bfoGVdgp6EXZ5dLT1jE7g3LvQpump'},
        'TOKABU': {'ca': 'H8xQ6poBjB9DTPMDTKWzWPrnxu4bDEhybxiouF8Ppump'},
        'OMEGAX': {'ca': '4Aar9R14YMbEie6yh8WcH1gWXrBtfucoFjw6SpjXpump'},
        'HACHI': {'ca': 'AsrtqZiNYt3c6nNCtkj7abUrVc8APsFF37Wffq45rkVh'}
    }
    
    bt.run_all(coins)


if __name__ == "__main__":
    main()
