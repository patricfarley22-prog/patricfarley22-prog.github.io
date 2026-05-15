#!/usr/bin/env python3
"""
NANO-CAP MEME COIN SCREENER
Comprehensive filter system for coins under $10M market cap
- Social sentiment (organic vs paid shills)
- Volume/MCap ratio analysis
- Developer/Partnership verification
- Utility vs Pure Meme classifier
- On-chain whale tracking
- OpenClaw integration for alerts
"""

import json
import math
import random
from datetime import datetime
from typing import List, Dict, Optional
import requests

DATA_DIR = "meme_coin_data"

class NanoCapScreener:
    """Master screener with all filters"""
    
    def __init__(self):
        self.results = []
        self.alerts = []
    
    # ============== SOCIAL SENTIMENT ==============
    
    def analyze_social_sentiment(self, coin: Dict) -> Dict:
        """
        Analyze social sentiment - organic vs paid shills
        Checks for:
        - Real community engagement
        - Developer activity
        - Partnership announcements
        - Natural conversation patterns
        """
        symbol = coin.get('symbol', '')
        name = coin.get('name', '')
        
        # Simulated social analysis (replace with real APIs)
        # In production: Twitter API, Discord bot, Telegram analysis
        
        # Organic growth indicators
        organic_indicators = {
            'dev_activity': random.random() > 0.3,  # Real devs posting updates
            'community_questions': random.randint(50, 5000),  # Real questions
            'partnership_mentions': random.randint(0, 10),
            'bot_ratio': random.uniform(0.1, 0.9),  # % of bot accounts
            'engagement_rate': random.uniform(0.01, 0.15),  # Likes/followers
        }
        
        # Shill detection
        shill_indicators = {
            'repetitive_posts': random.randint(10, 1000),
            'copy_paste_ratio': random.uniform(0.1, 0.8),
            'new_account_ratio': random.uniform(0.2, 0.9),
            'paid_promo_mentions': random.randint(0, 50),
        }
        
        # Score organic vs shill
        organic_score = (
            (1 - organic_indicators['bot_ratio']) * 30 +
            min(organic_indicators['engagement_rate'] * 100, 20) +
            (organic_indicators['dev_activity'] * 20) +
            min(organic_indicators['community_questions'] / 100, 15) +
            min(organic_indicators['partnership_mentions'] * 2, 15)
        )
        
        shill_score = (
            shill_indicators['copy_paste_ratio'] * 30 +
            shill_indicators['new_account_ratio'] * 25 +
            min(shill_indicators['paid_promo_mentions'] * 2, 25) +
            min(shill_indicators['repetitive_posts'] / 50, 20)
        )
        
        # Final sentiment score (0-100, higher = more organic)
        sentiment_score = max(0, min(100, organic_score - shill_score * 0.5))
        
        return {
            'organic_score': round(sentiment_score, 1),
            'bot_ratio': round(organic_indicators['bot_ratio'], 2),
            'engagement_rate': round(organic_indicators['engagement_rate'], 3),
            'dev_active': organic_indicators['dev_activity'],
            'partnerships': organic_indicators['partnership_mentions'],
            'shill_score': round(shill_score, 1),
            'verdict': 'ORGANIC' if sentiment_score > 60 else 'MIXED' if sentiment_score > 30 else 'PAID_SHILLS'
        }
    
    # ============== VOLUME/MCAP RATIO ==============
    
    def analyze_volume_mcap(self, coin: Dict) -> Dict:
        """
        Volume to Market Cap ratio analysis
        - Healthy ratio: 0.05-0.5 (5%-50% daily volume vs mcap)
        - Spike detection: Sudden volume increases
        - Sustainability: Consistent volume over time
        """
        mcap = coin.get('market_cap', 1)
        volume_24h = coin.get('volume_24h', 0)
        
        if mcap <= 0:
            return {'error': 'Invalid market cap'}
        
        ratio = volume_24h / mcap
        
        # Volume spike detection (compare to average)
        # In production: compare to 7-day average
        avg_volume = volume_24h * random.uniform(0.3, 1.5)  # Simulated baseline
        spike_ratio = volume_24h / avg_volume if avg_volume > 0 else 1.0
        
        # Classification
        if ratio > 0.5:
            health = "HYPERACTIVE"
            risk = "EXTREME"  # Possible pump/dump
        elif ratio > 0.2:
            health = "VERY_HIGH"
            risk = "HIGH"  # Active trading, volatile
        elif ratio > 0.05:
            health = "HEALTHY"
            risk = "MEDIUM"  # Normal activity
        elif ratio > 0.01:
            health = "LOW"
            risk = "LOW"  # Low liquidity
        else:
            health = "ILLIQUID"
            risk = "EXTREME"  # Can't exit easily
        
        # Spike alert
        spike_alert = spike_ratio > 2.0
        
        return {
            'volume_mcap_ratio': round(ratio, 4),
            'volume_24h': volume_24h,
            'mcap': mcap,
            'health': health,
            'risk': risk,
            'spike_ratio': round(spike_ratio, 2),
            'spike_alert': spike_alert,
            'verdict': 'SPIKE' if spike_alert else health
        }
    
    # ============== DEVELOPER/PARTNERSHIP CHECK ==============
    
    def verify_developer_partnerships(self, coin: Dict) -> Dict:
        """
        Check for real developers and partnerships
        - GitHub activity
        - Team doxxing
        - Partnership announcements
        - Contract verification
        """
        symbol = coin.get('symbol', '')
        
        # Simulated verification (replace with real checks)
        verification = {
            'github_active': random.random() > 0.7,  # Real code commits
            'contract_verified': random.random() > 0.5,  # Contract audited
            'team_doxxed': random.random() > 0.8,  # Team identity known
            'partnerships_real': random.randint(0, 5),
            'dev_responsive': random.random() > 0.6,  # Dev answers questions
        }
        
        # Score
        score = 0
        if verification['github_active']: score += 25
        if verification['contract_verified']: score += 20
        if verification['team_doxxed']: score += 25
        score += min(verification['partnerships_real'] * 5, 15)
        if verification['dev_responsive']: score += 15
        
        return {
            'legitimacy_score': score,
            'github_active': verification['github_active'],
            'contract_verified': verification['contract_verified'],
            'team_doxxed': verification['team_doxxed'],
            'partnerships': verification['partnerships_real'],
            'dev_responsive': verification['dev_responsive'],
            'verdict': 'LEGIT' if score >= 70 else 'SUSPECT' if score >= 40 else 'RUG_RISK'
        }
    
    # ============== UTILITY VS MEME CLASSIFIER ==============
    
    def classify_utility(self, coin: Dict) -> Dict:
        """
        Classify if coin has real utility or pure meme
        - Whitepaper analysis
        - Use case documentation
        - Roadmap progress
        - Real-world application
        """
        name = coin.get('name', '').lower()
        symbol = coin.get('symbol', '').lower()
        
        # Pure meme keywords
        pure_meme_keywords = ['doge', 'shib', 'pepe', 'bonk', 'wojak', 'troll', 
                           'inu', 'elon', 'musk', 'chad', 'based', 'moon']
        
        # Utility keywords
        utility_keywords = ['dao', 'defi', 'bridge', 'oracle', 'layer', 'protocol',
                          'swap', 'stake', 'yield', 'governance', 'infrastructure']
        
        meme_score = sum(1 for kw in pure_meme_keywords if kw in name or kw in symbol)
        utility_score = sum(1 for kw in utility_keywords if kw in name)
        
        # Simulated deeper analysis
        has_whitepaper = random.random() > 0.7
        has_roadmap = random.random() > 0.6
        functional_product = random.random() > 0.8
        revenue_model = random.random() > 0.9
        
        # Final classification
        if meme_score >= 2 and utility_score == 0:
            classification = "PURE_MEME"
        elif meme_score >= 1 and utility_score >= 1:
            classification = "MEME_UTILITY"
        elif utility_score >= 2 or (has_whitepaper and has_roadmap):
            classification = "UTILITY"
        else:
            classification = "SPECULATIVE"
        
        # Quality score
        quality = 0
        if has_whitepaper: quality += 20
        if has_roadmap: quality += 15
        if functional_product: quality += 30
        if revenue_model: quality += 20
        quality += min(utility_score * 10, 15)
        
        return {
            'classification': classification,
            'quality_score': quality,
            'has_whitepaper': has_whitepaper,
            'has_roadmap': has_roadmap,
            'functional_product': functional_product,
            'revenue_model': revenue_model,
            'meme_score': meme_score,
            'utility_score': utility_score,
            'verdict': 'REAL_PROJECT' if classification in ['UTILITY', 'MEME_UTILITY'] else 'PUMPAMENTAL'
        }
    
    # ============== ON-CHAIN WHALE TRACKER ==============
    
    def track_whales(self, coin: Dict) -> Dict:
        """
        On-chain whale tracking
        - Large holder movements
        - Accumulation vs Distribution
        - Wallet concentration
        - Smart money flow
        """
        mcap = coin.get('market_cap', 1)
        
        # Simulated on-chain data (replace with Solscan/Helius APIs)
        whale_data = {
            'top_10_holdings': random.uniform(0.3, 0.9),  # % held by top 10 wallets
            'whale_wallets': random.randint(5, 100),  # Wallets with >1% supply
            'recent_large_buys': random.randint(0, 50),
            'recent_large_sells': random.randint(0, 50),
            'smart_money_inflow': random.uniform(-100000, 500000),  # USD
            'new_wallets_24h': random.randint(10, 1000),
            'active_wallets_24h': random.randint(50, 5000),
        }
        
        # Net whale activity
        net_whales = whale_data['recent_large_buys'] - whale_data['recent_large_sells']
        
        # Concentration risk
        if whale_data['top_10_holdings'] > 0.8:
            concentration_risk = "EXTREME"  # Rug pull risk
        elif whale_data['top_10_holdings'] > 0.6:
            concentration_risk = "HIGH"
        elif whale_data['top_10_holdings'] > 0.4:
            concentration_risk = "MEDIUM"
        else:
            concentration_risk = "LOW"
        
        # Accumulation signal
        if net_whales > 20 and whale_data['smart_money_inflow'] > 100000:
            signal = "ACCUMULATING"
        elif net_whales < -20 and whale_data['smart_money_inflow'] < -50000:
            signal = "DISTRIBUTING"
        elif net_whales > 5:
            signal = "SLIGHT_BUY"
        elif net_whales < -5:
            signal = "SLIGHT_SELL"
        else:
            signal = "NEUTRAL"
        
        return {
            'whale_signal': signal,
            'net_whales': net_whales,
            'top_10_concentration': round(whale_data['top_10_holdings'], 2),
            'concentration_risk': concentration_risk,
            'smart_money_flow': round(whale_data['smart_money_inflow'], 0),
            'new_wallets_24h': whale_data['new_wallets_24h'],
            'active_wallets_24h': whale_data['active_wallets_24h'],
            'verdict': 'ACCUMULATE' if signal == 'ACCUMULATING' else 'CAUTION' if signal == 'DISTRIBUTING' else 'NEUTRAL'
        }
    
    # ============== MASTER SCREENING ==============
    
    def screen_coin(self, coin: Dict) -> Dict:
        """Run all filters on a single coin"""
        print(f"\n  Screening {coin['symbol']}...")
        
        # Run all analyses
        social = self.analyze_social_sentiment(coin)
        volume = self.analyze_volume_mcap(coin)
        dev = self.verify_developer_partnerships(coin)
        utility = self.classify_utility(coin)
        whales = self.track_whales(coin)
        
        # Combined score
        combined_score = (
            social['organic_score'] * 0.25 +
            (100 if volume['health'] == 'HEALTHY' else 50 if volume['health'] == 'LOW' else 20) * 0.20 +
            dev['legitimacy_score'] * 0.20 +
            utility['quality_score'] * 0.15 +
            (100 if whales['whale_signal'] == 'ACCUMULATING' else 50 if whales['whale_signal'] == 'NEUTRAL' else 20) * 0.20
        )
        
        # Final verdict
        if combined_score >= 70 and social['verdict'] == 'ORGANIC' and dev['verdict'] == 'LEGIT':
            verdict = "PASS"
            tier = "A"
        elif combined_score >= 50 and social['verdict'] != 'PAID_SHILLS':
            verdict = "PASS"
            tier = "B"
        elif combined_score >= 30:
            verdict = "WATCH"
            tier = "C"
        else:
            verdict = "FAIL"
            tier = "D"
        
        # Alert conditions
        alerts = []
        if volume['spike_alert']:
            alerts.append("VOLUME_SPIKE")
        if whales['whale_signal'] == 'ACCUMULATING':
            alerts.append("WHALE_ACCUMULATION")
        if social['verdict'] == 'PAID_SHILLS':
            alerts.append("SHILL_WARNING")
        if dev['verdict'] == 'RUG_RISK':
            alerts.append("RUG_RISK")
        
        return {
            'coin': coin,
            'social': social,
            'volume': volume,
            'dev': dev,
            'utility': utility,
            'whales': whales,
            'combined_score': round(combined_score, 1),
            'tier': tier,
            'verdict': verdict,
            'alerts': alerts
        }
    
    def screen_all(self, coins: List[Dict]) -> List[Dict]:
        """Screen multiple coins"""
        print("=" * 80)
        print("NANO-CAP MASTER SCREENER")
        print("Filters: Social | Volume | Dev | Utility | Whales")
        print("=" * 80)
        
        results = []
        for coin in coins:
            result = self.screen_coin(coin)
            results.append(result)
        
        # Sort by combined score
        results.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return results
    
    def display(self, results: List[Dict]):
        """Display screening results"""
        if not results:
            print("\nNo coins to display")
            return
        
        print("\n" + "=" * 80)
        print("SCREENING RESULTS")
        print("=" * 80)
        
        # Summary table
        print(f"\n{'#':<4} {'Symbol':<10} {'Tier':<6} {'Score':<8} {'Social':<8} {'Vol':<8} {'Dev':<8} {'Utility':<8} {'Whales':<10} {'Verdict':<8}")
        print("-" * 85)
        
        for i, r in enumerate(results[:15], 1):
            print(f"{i:<4} {r['coin']['symbol']:<10} {r['tier']:<6} {r['combined_score']:<7.1f} "
                  f"{r['social']['verdict'][:7]:<8} {r['volume']['health']:<8} {r['dev']['verdict']:<8} "
                  f"{r['utility']['classification']:<8} {r['whales']['whale_signal']:<10} {r['verdict']:<8}")
        
        # Passed coins
        passed = [r for r in results if r['verdict'] == 'PASS']
        if passed:
            print(f"\n{'='*80}")
            print(f"PASSED COINS: {len(passed)}")
            print(f"{'='*80}")
            
            for r in passed:
                print(f"\n  {r['coin']['symbol']} - {r['coin']['name']} (Tier {r['tier']})")
                print(f"    Score: {r['combined_score']:.1f}/100")
                print(f"    Social: {r['social']['verdict']} ({r['social']['organic_score']:.0f}% organic)")
                print(f"    Volume/MCap: {r['volume']['volume_mcap_ratio']:.2%} ({r['volume']['health']})")
                print(f"    Dev: {r['dev']['verdict']} (Score: {r['dev']['legitimacy_score']})")
                print(f"    Utility: {r['utility']['classification']} (Quality: {r['utility']['quality_score']})")
                print(f"    Whales: {r['whales']['whale_signal']} (Risk: {r['whales']['concentration_risk']})")
                
                if r['alerts']:
                    print(f"    ALERTS: {', '.join(r['alerts'])}")
        
        # Alerts summary
        all_alerts = []
        for r in results:
            all_alerts.extend(r['alerts'])
        
        if all_alerts:
            from collections import Counter
            alert_counts = Counter(all_alerts)
            
            print(f"\n{'='*80}")
            print("ALERTS SUMMARY")
            print(f"{'='*80}")
            for alert, count in alert_counts.most_common():
                print(f"  {alert}: {count} coins")
        
        # Stats
        print(f"\n{'='*80}")
        print("STATISTICS")
        print(f"{'='*80}")
        print(f"  Total screened: {len(results)}")
        print(f"  Passed: {len(passed)} ({len(passed)/len(results)*100:.0f}%)")
        print(f"  Watch: {len([r for r in results if r['verdict'] == 'WATCH'])}")
        print(f"  Failed: {len([r for r in results if r['verdict'] == 'FAIL'])}")
        print(f"  Tier A: {len([r for r in results if r['tier'] == 'A'])}")
        print(f"  Tier B: {len([r for r in results if r['tier'] == 'B'])}")


# ============== OPENCLAW INTEGRATION ==============

def generate_openclaw_alerts(results: List[Dict]):
    """Generate alerts for OpenClaw notification system"""
    alerts = []
    
    for r in results:
        if r['verdict'] == 'PASS' and r['tier'] == 'A':
            alerts.append({
                'type': 'TIER_A_COIN',
                'symbol': r['coin']['symbol'],
                'score': r['combined_score'],
                'message': f"{r['coin']['symbol']} passed all filters with score {r['combined_score']:.1f}",
                'urgency': 'HIGH'
            })
        
        if 'WHALE_ACCUMULATION' in r['alerts']:
            alerts.append({
                'type': 'WHALE_ALERT',
                'symbol': r['coin']['symbol'],
                'message': f"Whales accumulating {r['coin']['symbol']}",
                'urgency': 'MEDIUM'
            })
        
        if 'VOLUME_SPIKE' in r['alerts']:
            alerts.append({
                'type': 'VOLUME_SPIKE',
                'symbol': r['coin']['symbol'],
                'message': f"Volume spike detected on {r['coin']['symbol']}",
                'urgency': 'MEDIUM'
            })
    
    return alerts


def main():
    # Test coins (your nano-cap list)
    test_coins = [
        {"symbol": "TROLL", "name": "Troll", "market_cap": 5800000, "price": 0.1157, 
         "change_24h": -13.27, "change_7d": -20.0, "volume_24h": 6340000},
        {"symbol": "DOWGE", "name": "Dowge", "market_cap": 3200000, "price": 0.00321,
         "change_24h": -5.34, "change_7d": -8.0, "volume_24h": 22000},
        {"symbol": "WOBBLES", "name": "Wobbles", "market_cap": 910000, "price": 0.00091,
         "change_24h": -19.49, "change_7d": -25.0, "volume_24h": 90000},
        {"symbol": "PENGO", "name": "Pengo", "market_cap": 590000, "price": 0.00059,
         "change_24h": -2.38, "change_7d": -5.0, "volume_24h": 12000},
        {"symbol": "TOKABU", "name": "Tokabu", "market_cap": 2410000, "price": 0.00241,
         "change_24h": -15.49, "change_7d": -20.0, "volume_24h": 153000},
        {"symbol": "OMEGAX", "name": "OmegaX", "market_cap": 360000, "price": 0.00036,
         "change_24h": -1.73, "change_7d": 0.0, "volume_24h": 3000},
        {"symbol": "HACHI", "name": "Hachi", "market_cap": 22000, "price": 0.000022,
         "change_24h": -2.90, "change_7d": -5.0, "volume_24h": 500},
        {"symbol": "MARMUS", "name": "Chad Marmus", "market_cap": 3651, "price": 0.00000365,
         "change_24h": -90.1, "change_7d": 0.0, "volume_24h": 166136}
    ]
    
    print("\nNano-Cap Master Screener")
    print("=" * 80)
    
    screener = NanoCapScreener()
    results = screener.screen_all(test_coins)
    screener.display(results)
    
    # Generate OpenClaw alerts
    alerts = generate_openclaw_alerts(results)
    
    if alerts:
        print(f"\n{'='*80}")
        print(f"OPENCLAW ALERTS: {len(alerts)}")
        print(f"{'='*80}")
        for alert in alerts:
            print(f"\n  [{alert['urgency']}] {alert['type']}")
            print(f"    {alert['message']}")
    
    # Save
    import os
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/nano_cap_screened.json", "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "count": len(results),
            "passed": len([r for r in results if r['verdict'] == 'PASS']),
            "results": results,
            "alerts": alerts
        }, f, indent=2)
    
    print(f"\nSaved: {DATA_DIR}/nano_cap_screened.json")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
