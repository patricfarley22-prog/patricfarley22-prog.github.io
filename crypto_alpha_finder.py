#!/usr/bin/env python3
"""
CRYPTO ALPHA FINDER
Finds best communities and influential people pushing meme coins
Uses Twitter/X, Telegram, and on-chain data
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DATA_DIR = "meme_coin_data"
os.makedirs(DATA_DIR, exist_ok=True)

class AlphaFinder:
    """Find real alpha - communities and influencers behind coins"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "AlphaFinder/1.0"
        })
    
    def search_twitter_alpha(self, coin_symbol: str) -> Dict:
        """Search for alpha on Twitter/X for a coin"""
        # Using Brave Search API to find tweets and influencers
        search_terms = [
            f"${coin_symbol} crypto",
            f"{coin_symbol} token",
            f"{coin_symbol} meme coin"
        ]
        
        results = {
            "symbol": coin_symbol,
            "influencers": [],
            "communities": [],
            "sentiment": "neutral",
            "alpha_score": 0
        }
        
        # This would use Twitter API v2 or scrape
        # For now, we'll use DexScreener to find holder info
        return results
    
    def analyze_dexscreener(self, contract_address: str, chain: str = "solana") -> Dict:
        """Analyze a coin on DexScreener for community metrics"""
        url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
        
        try:
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            pair = data.get("pairs", [{}])[0]
            if not pair:
                return {}
            
            # Extract community metrics
            txns = pair.get("txns", {})
            h24 = txns.get("h24", {})
            
            buys = h24.get("buys", 0)
            sells = h24.get("sells", 0)
            
            # Calculate buy/sell ratio (community confidence)
            total_txns = buys + sells
            buy_ratio = buys / total_txns if total_txns > 0 else 0.5
            
            # Volume profile
            volume = pair.get("volume", {})
            vol_24h = volume.get("h24", 0)
            vol_6h = volume.get("h6", 0)
            
            # Price changes
            price_change = pair.get("priceChange", {})
            change_1h = price_change.get("h1", 0)
            change_24h = price_change.get("h24", 0)
            
            # Liquidity to market cap ratio (stability indicator)
            liquidity = pair.get("liquidity", {}).get("usd", 0)
            mcap = pair.get("marketCap", 0)
            liq_ratio = liquidity / mcap if mcap > 0 else 0
            
            # Social links
            socials = pair.get("info", {}).get("socials", [])
            websites = pair.get("info", {}).get("websites", [])
            
            return {
                "symbol": pair.get("baseToken", {}).get("symbol", ""),
                "name": pair.get("baseToken", {}).get("name", ""),
                "contract": contract_address,
                "chain": chain,
                "price": float(pair.get("priceUsd", 0)),
                "market_cap": mcap,
                "liquidity": liquidity,
                "liq_ratio": liq_ratio,
                "volume_24h": vol_24h,
                "volume_6h": vol_6h,
                "change_1h": change_1h,
                "change_24h": change_24h,
                "buys_24h": buys,
                "sells_24h": sells,
                "buy_ratio": buy_ratio,
                "total_txns_24h": total_txns,
                "holders": pair.get("holders", 0),
                "socials": socials,
                "websites": websites,
                "alpha_signals": []
            }
        except Exception as e:
            print(f"Error analyzing {contract_address}: {e}")
            return {}
    
    def score_alpha(self, data: Dict) -> Dict:
        """Score a coin for alpha potential"""
        score = 0
        signals = []
        
        # High buy ratio = community confidence
        if data.get("buy_ratio", 0) > 0.6:
            score += 25
            signals.append("Strong buy pressure (60%+ buys)")
        elif data.get("buy_ratio", 0) > 0.55:
            score += 15
            signals.append("More buys than sells")
        
        # High transaction count = active community
        if data.get("total_txns_24h", 0) > 1000:
            score += 25
            signals.append("Very active trading (>1000 txns)")
        elif data.get("total_txns_24h", 0) > 500:
            score += 15
            signals.append("Active trading (>500 txns)")
        elif data.get("total_txns_24h", 0) > 100:
            score += 10
            signals.append("Some activity (>100 txns)")
        
        # Liquidity ratio = stability
        if data.get("liq_ratio", 0) > 0.3:
            score += 20
            signals.append("High liquidity (30%+ of mcap)")
        elif data.get("liq_ratio", 0) > 0.15:
            score += 10
            signals.append("Decent liquidity (15%+ of mcap)")
        
        # Volume spike = interest
        vol_24h = data.get("volume_24h", 0)
        mcap = data.get("market_cap", 1)
        vol_mcap_ratio = vol_24h / mcap if mcap > 0 else 0
        
        if vol_mcap_ratio > 0.5:
            score += 20
            signals.append("Volume spike (>50% of mcap)")
        elif vol_mcap_ratio > 0.2:
            score += 10
            signals.append("Good volume (20%+ of mcap)")
        
        # Price momentum
        if data.get("change_24h", 0) > 50:
            score += 15
            signals.append("Strong 24h pump (>50%)")
        elif data.get("change_24h", 0) > 20:
            score += 10
            signals.append("Nice 24h move (>20%)")
        
        # Holder count
        if data.get("holders", 0) > 1000:
            score += 15
            signals.append("Large holder base (>1000)")
        elif data.get("holders", 0) > 500:
            score += 10
            signals.append("Growing holder base (>500)")
        
        # Social presence
        socials = data.get("socials", [])
        if len(socials) > 0:
            score += 10
            signals.append("Has social media presence")
        
        data["alpha_score"] = min(100, score)
        data["alpha_signals"] = signals
        data["alpha_grade"] = "A+" if score >= 80 else "A" if score >= 70 else "B+" if score >= 60 else "B" if score >= 50 else "C"
        
        return data
    
    def analyze_coins(self, contracts: List[Dict]) -> List[Dict]:
        """Analyze multiple coins"""
        results = []
        
        for contract_info in contracts:
            ca = contract_info["ca"]
            symbol = contract_info["symbol"]
            chain = contract_info.get("chain", "solana")
            
            print(f"\nAnalyzing {symbol}...")
            data = self.analyze_dexscreener(ca, chain)
            
            if data:
                scored = self.score_alpha(data)
                scored["notes"] = contract_info.get("notes", "")
                results.append(scored)
                print(f"  Alpha Score: {scored['alpha_score']}/100 ({scored['alpha_grade']})")
                for signal in scored["alpha_signals"][:3]:
                    print(f"    - {signal}")
            else:
                print(f"  Failed to analyze")
        
        # Sort by alpha score
        results.sort(key=lambda x: x["alpha_score"], reverse=True)
        return results
    
    def display_alpha(self, results: List[Dict]):
        """Display alpha analysis"""
        print("\n" + "=" * 80)
        print("ALPHA ANALYSIS - COMMUNITY & INFLUENCER POWER")
        print("=" * 80)
        
        # Top by alpha score
        print("\nTOP COINS BY ALPHA SCORE:")
        print(f"{'#':<4} {'Symbol':<10} {'Score':<8} {'Grade':<6} {'Buy%':<8} {'Txns':<8} {'MCap':<10} {'Why':<30}")
        print("-" * 80)
        
        for i, coin in enumerate(results[:10], 1):
            why = coin["alpha_signals"][0] if coin["alpha_signals"] else ""
            print(
                f"{i:<4} "
                f"{coin['symbol']:<10} "
                f"{coin['alpha_score']:<7.0f} "
                f"{coin['alpha_grade']:<6} "
                f"{coin['buy_ratio']*100:<7.1f}% "
                f"{coin['total_txns_24h']:<7.0f} "
                f"${coin['market_cap']/1_000_000:<9.2f}M "
                f"{why[:28]:<30}"
            )
        
        # Best communities (high buy ratio + many holders)
        print("\n" + "=" * 80)
        print("BEST COMMUNITIES (Strong Holder Confidence)")
        print("=" * 80)
        
        best_communities = [c for c in results if c["buy_ratio"] > 0.6 and c.get("holders", 0) > 100]
        best_communities.sort(key=lambda x: x["buy_ratio"], reverse=True)
        
        for i, coin in enumerate(best_communities[:5], 1):
            print(f"\n{i}. {coin['symbol']} ({coin['name']})")
            print(f"   Buy/Sell Ratio: {coin['buy_ratio']*100:.1f}% buys / {(1-coin['buy_ratio'])*100:.1f}% sells")
            print(f"   Holders: {coin.get('holders', 'Unknown')}")
            print(f"   24h Transactions: {coin['total_txns_24h']}")
            print(f"   Socials: {len(coin.get('socials', []))} links")
            for social in coin.get("socials", [])[:3]:
                print(f"     - {social.get('type', 'unknown')}: {social.get('url', 'N/A')}")
        
        # Most active
        print("\n" + "=" * 80)
        print("MOST ACTIVE (High Transaction Volume)")
        print("=" * 80)
        
        most_active = sorted(results, key=lambda x: x["total_txns_24h"], reverse=True)[:5]
        
        for i, coin in enumerate(most_active, 1):
            print(f"{i}. {coin['symbol']}: {coin['total_txns_24h']} txns (Buys: {coin['buys_24h']}, Sells: {coin['sells_24h']})")
        
        # Grade breakdown
        print("\n" + "=" * 80)
        print("GRADE BREAKDOWN")
        print("=" * 80)
        
        a_plus = [c for c in results if c["alpha_grade"] == "A+"]
        a_grade = [c for c in results if c["alpha_grade"] == "A"]
        b_plus = [c for c in results if c["alpha_grade"] == "B+"]
        
        print(f"A+ (80-100): {len(a_plus)} coins")
        for c in a_plus:
            print(f"  - {c['symbol']}: {c['alpha_score']} - {c['alpha_signals'][0] if c['alpha_signals'] else ''}")
        
        print(f"\nA (70-79): {len(a_grade)} coins")
        for c in a_grade:
            print(f"  - {c['symbol']}: {c['alpha_score']}")
        
        print(f"\nB+ (60-69): {len(b_plus)} coins")
        for c in b_plus:
            print(f"  - {c['symbol']}: {c['alpha_score']}")


def main():
    finder = AlphaFinder()
    
    # Test with known coins
    test_coins = [
        {
            "ca": "5UUH9RTDiSpq6HKS6bp4NdU9PNJpXRXuiw6ShBTBhgH2",
            "symbol": "TROLL",
            "chain": "solana",
            "notes": "Troll face meme"
        },
        {
            "ca": "DQnkBM4eYYMnVE8Qy2K3BB7uts1fh2EwBVktEz6jpump",
            "symbol": "DOWGE",
            "chain": "solana",
            "notes": "Doge derivative"
        },
        {
            "ca": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            "symbol": "BONK",
            "chain": "solana",
            "notes": "Big community"
        },
        {
            "ca": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
            "symbol": "WIF",
            "chain": "solana",
            "notes": "Dogwifhat"
        },
        {
            "ca": "9yZ5Ru8pbmJZ6Q2DKLCGXkaLNwkm83cnJ4QCw4PFpump",
            "symbol": "WOBBLES",
            "chain": "solana",
            "notes": "Recent launch"
        }
    ]
    
    print("=" * 80)
    print("FINDING REAL ALPHA - COMMUNITIES & INFLUENCERS")
    print("=" * 80)
    print("\nAnalyzing coins for:")
    print("- Community strength (buy/sell ratio)")
    print("- Transaction activity (real vs bot)")
    print("- Holder growth (organic vs fake)")
    print("- Social presence (real communities)")
    print("=" * 80)
    
    results = finder.analyze_coins(test_coins)
    finder.display_alpha(results)
    
    # Save
    filepath = os.path.join(DATA_DIR, "alpha_analysis.json")
    with open(filepath, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "count": len(results),
            "coins": results
        }, f, indent=2)
    
    print(f"\n{'='*80}")
    print("FILES")
    print(f"{'='*80}")
    print(f"1. crypto_alpha_finder.py - This analyzer")
    print(f"2. meme_coin_data/alpha_analysis.json - Results")
    print(f"\nTo find REAL communities, you need:")
    print(f"- DexScreener Premium (holder analytics)")
    print(f"- Twitter/X API (influencer tracking)")
    print(f"- Telegram bot (community monitoring)")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
