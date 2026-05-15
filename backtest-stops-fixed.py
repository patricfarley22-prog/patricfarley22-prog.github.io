#!/usr/bin/env python3
"""
BACKTESTER WITH STOP LOSSES - FIXED
Tests quantum signals with risk management
"""

import json
import os

class BacktestWithStops:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
    
    def load_data(self, symbol):
        filepath = f'meme_coin_data/{symbol}_history.json'
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def generate_signal(self, history, index):
        if index < 14:
            return 'HOLD', 0.25
        
        current = history[index]
        price = current['price']
        
        price_1d = history[index-1]['price']
        price_3d = history[index-3]['price']
        price_7d = history[index-7]['price']
        price_14d = history[index-14]['price']
        
        ret_1d = ((price - price_1d) / price_1d * 100) if price_1d > 0 else 0
        ret_3d = ((price - price_3d) / price_3d * 100) if price_3d > 0 else 0
        ret_7d = ((price - price_7d) / price_7d * 100) if price_7d > 0 else 0
        ret_14d = ((price - price_14d) / price_14d * 100) if price_14d > 0 else 0
        
        vol_now = current['volume']
        vol_avg = sum(h['volume'] for h in history[max(0,index-7):index]) / 7
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 1
        
        signal = 'HOLD'
        confidence = 0.25
        
        oversold = ret_14d < -25 and ret_7d > -5
        overbought = ret_14d > 40 and ret_7d < 5
        
        if oversold and vol_ratio > 1.2:
            signal = 'BUY'
            confidence = 0.35 + abs(ret_14d) / 100
        elif ret_7d > 10 and ret_1d > 0 and vol_ratio > 1.3:
            signal = 'BUY'
            confidence = 0.4 + ret_7d / 100
        elif ret_7d > 20:
            signal = 'BUY'
            confidence = 0.5
        elif overbought and vol_ratio > 1.2:
            signal = 'SELL'
            confidence = 0.35 + abs(ret_14d) / 100
        elif ret_7d < -10 and ret_1d < 0 and vol_ratio > 1.3:
            signal = 'SELL'
            confidence = 0.4 + abs(ret_7d) / 100
        elif ret_7d < -20:
            signal = 'SELL'
            confidence = 0.5
        elif abs(ret_1d) > 8 and vol_ratio > 2:
            signal = 'BUY' if ret_1d > 0 else 'SELL'
            confidence = 0.4 + abs(ret_1d) / 50
        
        confidence = min(0.6, confidence)
        return signal, confidence
    
    def backtest(self, symbol, threshold=0.30, position_size=0.25, stop_loss=-0.08):
        data = self.load_data(symbol)
        if not data or 'history' not in data:
            return None
        
        history = data['history']
        if len(history) < 30:
            return None
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity = [capital]
        stop_hits = 0
        
        for i in range(14, len(history)):
            signal, confidence = self.generate_signal(history, i)
            price = history[i]['price']
            date = history[i].get('date', '')
            
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
                        'date': date,
                        'pnl_pct': pnl_pct_real
                    })
                    stop_hits += 1
                    position = 0
                    entry_price = 0
                    continue
            
            if confidence >= threshold:
                if signal == 'BUY' and position == 0:
                    invest = capital * position_size
                    shares = invest / price
                    position = shares
                    entry_price = price
                    capital -= invest
                    trades.append({'type': 'BUY', 'price': price, 'date': date, 'value': invest})
                elif signal == 'SELL' and position > 0:
                    sell_val = position * price
                    pnl = sell_val - trades[-1]['value']
                    pnl_pct = (pnl / trades[-1]['value']) * 100
                    capital += sell_val
                    trades.append({'type': 'SELL', 'price': price, 'date': date, 'pnl_pct': pnl_pct})
                    position = 0
                    entry_price = 0
            
            equity.append(capital + (position * price))
        
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
            'trade_list': trades
        }
    
    def run_all(self, symbols):
        print("=" * 80)
        print("BACKTESTER WITH STOP LOSSES")
        print("=" * 80)
        
        results = []
        for symbol in symbols:
            r = self.backtest(symbol)
            if r:
                results.append(r)
                status = "PROFIT" if r['return'] > 0 else "LOSS"
                print(f"\n{status}: {r['symbol']}")
                print(f"  Return: {r['return']:+.2f}% | Trades: {r['trades']} (W:{r['wins']} S:{r['stops']})")
                print(f"  Win Rate: {r['win_rate']:.1f}% | Max DD: {r['max_dd']:.2f}%")
        
        if results:
            avg_ret = sum(r['return'] for r in results) / len(results)
            print(f"\nAverage Return: {avg_ret:+.2f}%")
            ranked = sorted(results, key=lambda x: x['return'], reverse=True)
            print("\nRanked:")
            for i, r in enumerate(ranked[:10], 1):
                print(f"{i}. {r['symbol']}: {r['return']:+.2f}% ({r['trades']} trades)")
        
        return results


def main():
    bt = BacktestWithStops()
    symbols = ['BONK', 'FLOKI', 'PEPE', 'SHIB', 'DOGE']
    bt.run_all(symbols)

if __name__ == "__main__":
    main()
