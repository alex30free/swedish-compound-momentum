#!/usr/bin/env python3
"""
Compound Momentum Screener for Swedish Stocks
============================================
Ranks all OMX Stockholm stocks by COMPOUND MOMENTUM SCORE:
    Score = Return(3M) + Return(6M) + Return(12M)

Each return is the raw percentage price change over the window.
Top 20 stocks by compound score are saved to momentum_data.json.

Updated every Friday evening after Nasdaq Stockholm closes,
via GitHub Actions (.github/workflows/update_momentum.yml).
"""

import json
import os
import time
import datetime
import warnings
warnings.filterwarnings("ignore")

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("ERROR: Run: pip install yfinance pandas")
    raise
from fetch_swedish_tickers import get_tickers


# ─────────────────────────────────────────────────────────────────────────────
# FULL SWEDISH STOCK UNIVERSE
# Source: Nasdaq OMX Stockholm (Large + Mid + Small Cap)
# ─────────────────────────────────────────────────────────────────────────────

TICKERS = get_tickers(verbose=True, max_pages=2)

# Deduplicate while preserving order
seen = set()
TICKERS_DEDUP = []
for item in TICKERS:
    if item[1] not in seen:
        seen.add(item[1])
        TICKERS_DEDUP.append(item)
TICKERS = TICKERS_DEDUP

OUTPUT_JSON    = "momentum_data.json"
PREV_RANKS_FILE = "momentum_prev_ranks.json"

# Approximate trading days per calendar period
DAYS_3M  = 65    # ~3 months
DAYS_6M  = 130   # ~6 months
DAYS_12M = 260   # ~12 months


def compute_momentum(name, symbol, prices):
    """
    Returns (mom_3m, mom_6m, mom_12m) as percentage returns, or None if data insufficient.
    """
    n = len(prices)
    if n < DAYS_12M + 5:
        return None

    price_now = float(prices.iloc[-1])

    def pct_return(days_back):
        idx = max(0, n - 1 - days_back)
        p_past = float(prices.iloc[idx])
        if p_past == 0 or p_past != p_past:  # guard div/0 and NaN
            return None
        return ((price_now / p_past) - 1.0) * 100.0

    m3  = pct_return(DAYS_3M)
    m6  = pct_return(DAYS_6M)
    m12 = pct_return(DAYS_12M)

    if m3 is None or m6 is None or m12 is None:
        return None

    return m3, m6, m12


def load_prev_ranks():
    if os.path.exists(PREV_RANKS_FILE):
        with open(PREV_RANKS_FILE) as f:
            return json.load(f)
    return {}


def save_prev_ranks(top20):
    ranks = {r["ticker"]: r["rank"] for r in top20}
    with open(PREV_RANKS_FILE, "w") as f:
        json.dump(ranks, f)


def main():
    now        = datetime.datetime.now(datetime.timezone.utc)
    end_date   = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=420)  # a little extra buffer

    total = len(TICKERS)

    print("=" * 65)
    print("  Compound Momentum Screener — OMX Stockholm")
    print("  Universe: " + str(total) + " tickers")
    print("  Running at: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("  Windows: 3M (" + str(DAYS_3M) + "d)  6M (" + str(DAYS_6M) + "d)  12M (" + str(DAYS_12M) + "d)")
    print("=" * 65)
    print("")

    results = []
    skipped = []

    for i, (name, symbol) in enumerate(TICKERS):
        print("[" + str(i + 1).rjust(3) + "/" + str(total) + "] " + symbol.ljust(20), end="", flush=True)

        try:
            stock = yf.Ticker(symbol)
            hist  = stock.history(
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                auto_adjust=True
            )

            if hist.empty or len(hist) == 0:
                skipped.append({"name": name, "ticker": symbol, "reason": "No price data", "days_available": 0})
                print("✗  No price data")
                time.sleep(0.3)
                continue

            prices = hist["Close"].dropna()
            days   = len(prices)

            mom = compute_momentum(name, symbol, prices)
            if mom is None:
                skipped.append({
                    "name": name, "ticker": symbol,
                    "reason": "Insufficient history (need " + str(DAYS_12M + 5) + "d, have " + str(days) + "d)",
                    "days_available": days
                })
                print("✗  Only " + str(days) + "/" + str(DAYS_12M + 5) + " trading days")
                time.sleep(0.3)
                continue

            m3, m6, m12 = mom
            compound = round(m3 + m6 + m12, 2)

            results.append({
                "name":           name,
                "ticker":         symbol,
                "price":          round(float(prices.iloc[-1]), 2),
                "mom_3m":         round(m3, 2),
                "mom_6m":         round(m6, 2),
                "mom_12m":        round(m12, 2),
                "compound_score": compound,
            })

            print("✓  3M=" + str(round(m3, 1)).rjust(7) + "%"
                  "  6M=" + str(round(m6, 1)).rjust(7) + "%"
                  "  12M=" + str(round(m12, 1)).rjust(7) + "%"
                  "  COMPOUND=" + str(compound).rjust(8) + "%")

        except Exception as e:
            skipped.append({"name": name, "ticker": symbol, "reason": "Error: " + str(e)[:60], "days_available": 0})
            print("✗  " + str(e)[:50])

        time.sleep(0.3)

    print("")
    print("-" * 65)
    print("  Valid: " + str(len(results)) + "  Skipped: " + str(len(skipped)))
    print("-" * 65)

    # Sort descending by compound score
    results.sort(key=lambda x: x["compound_score"], reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    top20 = results[:20]

    # Attach previous ranks
    prev_ranks = load_prev_ranks()
    for r in top20:
        r["prev_rank"] = prev_ranks.get(r["ticker"], None)

    save_prev_ranks(top20)

    # Print top 20
    print("")
    print("=" * 65)
    print("  TOP 20 — COMPOUND MOMENTUM RANKING")
    print("=" * 65)
    for r in top20:
        prev = "(prev #" + str(r["prev_rank"]) + ")" if r["prev_rank"] else "(new)"
        print("  #" + str(r["rank"]).rjust(2)
              + "  " + r["name"].ljust(30)
              + "  Score=" + str(r["compound_score"]).rjust(8) + "%"
              + "  " + prev)

    # Write JSON
    output = {
        "updated":         now.strftime("%Y-%m-%d %H:%M UTC"),
        "total_attempted": len(TICKERS),
        "stocks_screened": len(results),
        "skipped_count":   len(skipped),
        "top20":           top20,
        "skipped":         skipped,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("")
    print("✅  Saved → " + OUTPUT_JSON)
    print("    Updated: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))


if __name__ == "__main__":
    main()
