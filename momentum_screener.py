#!/usr/bin/env python3
"""
Compound Momentum Screener for Swedish Stocks
============================================
Ranks all OMX Stockholm stocks by COMPOUND MOMENTUM SCORE:
Score = Return(3M) + Return(6M) + Return(12M)

Top 30 stocks by compound score are saved to momentum_data.json.
"""

import json, os, time, datetime, warnings
warnings.filterwarnings("ignore")

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("ERROR: Run: pip install yfinance pandas")
    raise

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
FILTER_BY_SIZE   = False
FILTER_BY_FSCORE = False
MIN_MARKET_CAP_MSEK = 500
MIN_FSCORE = 5

# ─── UNIVERSE ────────────────────────────────────────────────────────────────
TICKERS = [
    ("Lundin Mining", "LUMI.ST"), ("Boliden", "BOL.ST"), ("Nokia", "NOKIA-SEK.ST"),
    ("Cantargia", "CANTA.ST"), ("Orrön Energy", "ORRON.ST"), ("Ovzon", "OVZON.ST"),
    ("Cloetta", "CLA-B.ST"), ("Sandvik", "SAND.ST"), ("Studsvik", "SVIK.ST"),
    ("Attendo", "ATT.ST"), ("Acast", "ACAST.ST"), ("FM Mattsson", "FMM-B.ST"),
    ("Berner Industrier", "BERNER-B.ST"), ("Hanza", "HANZA.ST"), ("SSAB B", "SSAB-B.ST"),
    ("Inission", "INISS-B.ST"), ("Peab", "PEAB-B.ST"), ("Midsona B", "MSON-B.ST"),
    ("Swedish Orphan Biovitrum", "SOBI.ST"), ("Maha Capital", "MAHA-A.ST"),
    ("Instalco", "INSTAL.ST"), ("Munters", "MTRS.ST"), ("Revolutionrace", "RVRC.ST"),
    ("Ericsson B", "ERIC-B.ST"), ("Scandi Standard", "SCST.ST"), ("Wise Group", "WISE.ST"),
    ("Orexo", "ORX.ST"), ("Telia Company", "TELIA.ST"), ("Saab", "SAAB-B.ST"),
    ("Hexatronic", "HTRO.ST"), ("Eniro", "ENRO.ST"), ("Coor Service Management", "COOR.ST"),
    ("Lundin Gold", "LUG.ST"), ("Electrolux B", "ELUX-B.ST"),
    ("International Petroleum", "IPCO.ST"), ("Infrea", "INFREA.ST"),
    ("Elekta", "EKTA-B.ST"), ("Hennes & Mauritz", "HM-B.ST"), ("VBG Group", "VBG-B.ST"),
    ("Volvo Car", "VOLCAR-B.ST"), ("Epiroc B", "EPI-B.ST"), ("ABB", "ABB.ST"),
    ("Volvo B", "VOLV-B.ST"), ("Alligo", "ALLIGO-B.ST"), ("Meren Energy", "MER.ST"),
    ("Bufab", "BUFAB.ST"), ("Alfa Laval", "ALFA.ST"), ("Atlas Copco A", "ATCO-A.ST"),
    ("Prevas", "PREV-B.ST"), ("AstraZeneca", "AZN.ST"),
    ("Gruvaktiebolaget Viscaria", "VISC.ST"), ("Saniona", "SANION.ST"),
    ("Svedbergs Group", "SVED-B.ST"), ("Better Collective", "BETCO.ST"),
    ("Skanska", "SKA-B.ST"), ("Enad Global 7", "EG7.ST"), ("Gränges", "GRNG.ST"),
    ("Tele2 B", "TEL2-B.ST"), ("Bravida", "BRAV.ST"), ("TietoEVRY", "TIETOS.ST"),
    ("Rusta", "RUSTA.ST"), ("NCC B", "NCC-B.ST"), ("Synsam", "SYNSAM.ST"),
    ("Assa Abloy", "ASSA-B.ST"), ("Proact IT", "PACT.ST"), ("Alleima", "ALLEI.ST"),
    ("Nordisk Bergteknik", "NORB-B.ST"), ("NCAB Group", "NCAB.ST"),
    ("Xvivo Perfusion", "XVIVO.ST"), ("Clas Ohlson", "CLAS-B.ST"), ("Humana", "HUM.ST"),
    ("SkiStar", "SKIS-B.ST"), ("Duroc", "DURC-B.ST"), ("Stora Enso R", "STE-R.ST"),
    ("Bilia", "BILI-A.ST"), ("Byggmax", "BMAX.ST"), ("Securitas", "SECU-B.ST"),
    ("Railcare", "RAIL.ST"), ("Sdiptech", "SDIP-B.ST"), ("Axfood", "AXFO.ST"),
    ("NOTE", "NOTE.ST"), ("Essity B", "ESSITY-B.ST"), ("Cinclus Pharma", "CINPHA.ST"),
    ("BioGaia", "BIOG-B.ST"), ("Traton", "8TRA.ST"), ("Loomis", "LOOMIS.ST"),
    ("Moberg Pharma", "MOB.ST"), ("Duni", "DUNI.ST"), ("Hansa Biopharma", "HNSA.ST"),
    ("CTEK", "CTEK.ST"), ("Trelleborg", "TREL-B.ST"), ("Catena Media", "CTM.ST"),
    ("Björn Borg", "BORG.ST"), ("XANO Industri", "XANO-B.ST"), ("Gentoo Media", "G2M.ST"),
    ("Ambea", "AMBEA.ST"), ("SKF B", "SKF-B.ST"), ("Boozt", "BOOZT.ST"),
    ("OEM International", "OEM-B.ST"), ("AQ Group", "AQ.ST"),
    ("SynAct Pharma", "SYNACT.ST"), ("Beijer Alma", "BEIA-B.ST"), ("Mycronic", "MYCR.ST"),
    ("Ferronordic", "FNM.ST"), ("Addtech", "ADDT-B.ST"),
    ("Micro Systemation", "MSAB-B.ST"), ("AcadeMedia", "ACAD.ST"),
    ("mySafety", "SAFETY-B.ST"), ("Eltel", "ELTEL.ST"), ("BE Group", "BEGR.ST"),
    ("Systemair", "SYSR.ST"), ("JM", "JM.ST"), ("KnowIT", "KNOW.ST"),
    ("NIBE Industrier", "NIBE-B.ST"), ("Lagercrantz", "LAGR-B.ST"),
    ("Indutrade", "INDT.ST"), ("Nilörngruppen", "NIL-B.ST"), ("Actic Group", "ATIC.ST"),
    ("BHG Group", "BHG.ST"), ("Holmen B", "HOLM-B.ST"), ("Hexagon", "HEXA-B.ST"),
    ("Karnell Group", "KARNEL-B.ST"), ("Bong Ljungdahl", "BONG.ST"),
    ("Viaplay B", "VPLAY-B.ST"), ("Scandic Hotels", "SHOT.ST"),
    ("Malmbergs Elektriska", "MEAB-B.ST"), ("Invisio", "IVSO.ST"),
    ("Egetis Therapeutics", "EGTX.ST"), ("Episurf Medical", "EPIS-B.ST"),
    ("Getinge", "GETI-B.ST"), ("BioArctic", "BIOA-B.ST"),
    ("Electrolux Professional B", "EPRO-B.ST"), ("Sensys Gatso", "SGG.ST"),
    ("Moment Group", "MOMENT.ST"), ("SCA B", "SCA-B.ST"), ("Lifco", "LIFCO-B.ST"),
    ("Softronic", "SOF-B.ST"), ("Inwido", "INWI.ST"), ("HMS Networks", "HMS.ST"),
    ("Fenix Outdoor", "FOI-B.ST"), ("AAK", "AAK.ST"), ("Flerie", "FLERIE.ST"),
    ("CellaVision", "CEVI.ST"), ("New Wave", "NEWA-B.ST"), ("Hexpol", "HPOL-B.ST"),
    ("Fingerprint Cards", "FING-B.ST"), ("Elon", "ELON.ST"), ("Billerud", "BILL.ST"),
    ("Dustin Group", "DUST.ST"), ("Autoliv", "ALIV-SDB.ST"), ("Dedicare", "DEDI.ST"),
    ("Elanders", "ELAN-B.ST"), ("AFRY", "AFRY.ST"), ("Engcon", "ENGCON-B.ST"),
    ("Asmodee", "ASMDEE-B.ST"), ("Hacksaw", "HACK.ST"), ("Nolato", "NOLA-B.ST"),
    ("PION Group", "PION-B.ST"), ("Humble Group", "HUMBLE.ST"), ("Sweco B", "SWEC-B.ST"),
    ("Formpipe Software", "FPIP.ST"), ("Carasent", "CARA.ST"), ("Nederman", "NMAN.ST"),
    ("Modern Times Group B", "MTG-B.ST"), ("Viva Wine", "VIVA.ST"),
    ("Arctic Paper", "ARP.ST"), ("Anoto", "ANOT.ST"), ("TradeDoubler", "TRAD.ST"),
    ("Mildef Group", "MILDEF.ST"), ("Isofol Medical", "ISOFOL.ST"),
    ("Concejo B", "CNCJO-B.ST"), ("Bergman & Beving", "BERG-B.ST"),
    ("Vicore Pharma", "VICO.ST"), ("Eolus", "EOLU-B.ST"), ("Thule", "THULE.ST"),
    ("Beijer Ref", "BEIJ-B.ST"), ("AddLife", "ALIF-B.ST"), ("Kabe", "KABE-B.ST"),
    ("Vimian Group", "VIMIAN.ST"), ("Rejlers", "REJL-B.ST"),
    ("ITAB Shop Concept", "ITAB.ST"), ("MEKO", "MEKO.ST"), ("Sinch", "SINCH.ST"),
    ("Lindab", "LIAB.ST"), ("SinterCast", "SINT.ST"), ("Alimak", "ALIG.ST"),
    ("MedCap", "MCAP.ST"), ("PowerCell", "PCELL.ST"), ("Momentum Group", "MMGR-B.ST"),
    ("Sivers Semiconductors", "SIVE.ST"), ("Medicover", "MCOV-B.ST"),
    ("RaySearch Laboratories", "RAY-B.ST"), ("Ependion", "EPEN.ST"),
    ("Novotek", "NTEK-B.ST"), ("BICO Group", "BICO.ST"), ("Stillfront", "SF.ST"),
    ("Enea", "ENEA.ST"), ("Husqvarna B", "HUSQ-B.ST"), ("C-RAD", "CRAD-B.ST"),
    ("Arjo", "ARJO-B.ST"), ("Bulten", "BULTEN.ST"), ("Bioinvent", "BINV.ST"),
    ("Arla Plast", "ARPL.ST"), ("Lammhults Design", "LAMM-B.ST"),
    ("Cavotec", "CCC.ST"), ("Medivir", "MVIR.ST"), ("Nelly Group", "NELLY.ST"),
    ("Wall to Wall", "WTW-A.ST"), ("Pierce Group", "PIERCE.ST"),
    ("Green Landscaping", "GREEN.ST"), ("Precise Biometrics", "PREC.ST"),
    ("Evolution", "EVO.ST"), ("Dometic", "DOM.ST"), ("Dynavox Group", "DYVOX.ST"),
    ("Troax Group", "TROAX.ST"), ("BTS Group", "BTS-B.ST"), ("Fagerhult", "FAG.ST"),
    ("Vitrolife", "VITR.ST"), ("Rottneros", "RROS.ST"), ("Vitec Software", "VIT-B.ST"),
    ("Ascelia Pharma", "ACE.ST"), ("EQL Pharma", "EQL.ST"), ("Senzime", "SEZI.ST"),
    ("Balco Group", "BALCO.ST"), ("Boule Diagnostics", "BOUL.ST"),
    ("Infant Bacterial", "IBT-B.ST"), ("Camurus", "CAMX.ST"), ("Garo", "GARO.ST"),
    ("B3 Consulting", "B3.ST"), ("Asker Healthcare", "ASKER.ST"),
    ("Sedana Medical", "SEDANA.ST"), ("ProfilGruppen", "PROF-B.ST"),
    ("Fasadgruppen", "FG.ST"), ("Karnov", "KAR.ST"), ("Bonesupport", "BONEX.ST"),
    ("Pricer", "PRIC-B.ST"), ("Lime Technologies", "LIME.ST"), ("Addnode", "ANOD-B.ST"),
    ("Mendus", "IMMU.ST"), ("CoinShares", "CS.ST"), ("Betsson", "BETS-B.ST"),
    ("Apotea", "APOTEA.ST"), ("CTT Systems", "CTT.ST"),
    ("IRLAB Therapeutics", "IRLAB-A.ST"), ("eWork", "EWRK.ST"), ("Mips", "MIPS.ST"),
    ("Sleep Cycle", "SLEEP.ST"), ("Sectra", "SECT-B.ST"), ("Bactiguard", "BACTI-B.ST"),
    ("Embracer", "EMBRAC-B.ST"), ("G5 Entertainment", "G5EN.ST"),
    ("Xspray Pharma", "XSPRAY.ST"), ("Profoto", "PRFO.ST"), ("Cint Group", "CINT.ST"),
    ("Tobii", "TOBII.ST"), ("Image Systems", "IS.ST"), ("Nobia", "NOBI.ST"),
    ("Q-Linea", "QLINEA.ST"), ("Net Insight", "NETI-B.ST"), ("Hemnet", "HEM.ST"),
    ("Starbreeze B", "STAR-B.ST"), ("Alvotech SDB", "ALVO-SDB.ST"),
    ("Transtema", "TRANS.ST"), ("Yubico", "YUBICO.ST"), ("Netel Holding", "NETEL.ST"),
    ("Vivesto", "VIVE.ST"), ("Oncopeptides", "ONCO.ST"), ("Nanologica", "NICA.ST"),
    ("Active Biotech", "ACTI.ST"), ("Truecaller", "TRUE-B.ST"),
    ("Immunovia", "IMMNOV.ST"), ("Wästbygg", "WBGR-B.ST"),
    ("Xbrane Biopharma", "XBRANE.ST"), ("Alligator Bioscience", "ATORX.ST"),
    ("Verisure", "VSURE.ST"),
]

OUTPUT_JSON     = "momentum_data.json"
PREV_RANKS_FILE = "momentum_prev_ranks.json"
DAYS_3M  = 65
DAYS_6M  = 130
DAYS_12M = 260
USD_TO_SEK = 10.5


def compute_fscore(info):
    score = 0
    avail = 0
    def safe(k): v = info.get(k); return v if v is not None and v == v else None

    ni = safe('netIncomeToCommon'); ta = safe('totalAssets')
    if ni is not None and ta and ta > 0:
        avail += 1
        if ni / ta > 0: score += 1
    ocf = safe('operatingCashflow')
    if ocf is not None:
        avail += 1
        if ocf > 0: score += 1
    if ocf is not None and ni is not None:
        avail += 1
        if ocf > ni: score += 1
    gm = safe('grossMargins')
    if gm is not None:
        avail += 1
        if gm > 0: score += 1
    td = safe('totalDebt') or 0
    if ta and ta > 0:
        avail += 1
        if (td / ta) < 0.6: score += 1
    cr = safe('currentRatio')
    if cr is not None:
        avail += 1
        if cr >= 1.0: score += 1
    so = safe('sharesOutstanding'); fs = safe('floatShares')
    if so and fs and so > 0:
        avail += 1
        if fs / so >= 0.80: score += 1
    om = safe('operatingMargins')
    if om is not None:
        avail += 1
        if om > 0: score += 1
    roe = safe('returnOnEquity')
    if roe is not None:
        avail += 1
        if roe > 0: score += 1
    return score if avail >= 5 else None


def get_market_cap_msek(info):
    mc = info.get('marketCap')
    if mc is None or mc != mc or mc <= 0: return None
    return (mc * USD_TO_SEK) / 1_000_000


def compute_momentum(prices):
    n = len(prices)
    if n < DAYS_12M + 5: return None
    p_now = float(prices.iloc[-1])
    def ret(d): p = float(prices.iloc[max(0, n-1-d)]); return None if p == 0 else ((p_now/p)-1)*100
    m3, m6, m12 = ret(DAYS_3M), ret(DAYS_6M), ret(DAYS_12M)
    return None if any(x is None for x in [m3,m6,m12]) else (m3, m6, m12)


def load_prev_ranks():
    return json.load(open(PREV_RANKS_FILE)) if os.path.exists(PREV_RANKS_FILE) else {}

def save_prev_ranks(top50):
    json.dump({r["ticker"]: r["rank"] for r in top50}, open(PREV_RANKS_FILE,"w"))


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=420)
    total = len(TICKERS)

    print("=" * 65)
    print("  Compound Momentum Screener — OMX Stockholm")
    print(f"  Universe: {total} tickers  |  Top 50 output")
    print(f"  Running at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 65 + "\n")

    results, skipped = [], []

    for i, (name, symbol) in enumerate(TICKERS):
        print(f"[{i+1:>3}/{total}] {symbol:<22}", end="", flush=True)
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date.strftime("%Y-%m-%d"),
                                 end=end_date.strftime("%Y-%m-%d"), auto_adjust=True)
            if hist.empty:
                skipped.append({"name":name,"ticker":symbol,"reason":"No price data","days_available":0})
                print("✗ No price data"); time.sleep(0.3); continue

            prices = hist["Close"].dropna()
            mom = compute_momentum(prices)
            if mom is None:
                skipped.append({"name":name,"ticker":symbol,
                                 "reason":f"Insufficient history (need {DAYS_12M+5}d, have {len(prices)}d)",
                                 "days_available":len(prices)})
                print(f"✗ Only {len(prices)}/{DAYS_12M+5} days"); time.sleep(0.3); continue

            m3, m6, m12 = mom
            compound = round(m3+m6+m12, 2)
            info = stock.info
            mcap = get_market_cap_msek(info)
            fscore = compute_fscore(info)

            if FILTER_BY_SIZE and (mcap is None or mcap < MIN_MARKET_CAP_MSEK):
                reason = "Filtered: market cap unavailable" if mcap is None else f"Filtered: {round(mcap)} MSEK < min {MIN_MARKET_CAP_MSEK} MSEK"
                skipped.append({"name":name,"ticker":symbol,"reason":reason,"days_available":len(prices)})
                print(f"✗ {reason}"); time.sleep(0.3); continue

            if FILTER_BY_FSCORE and (fscore is None or fscore < MIN_FSCORE):
                reason = "Filtered: F-Score unavailable" if fscore is None else f"Filtered: F-Score {fscore} < min {MIN_FSCORE}"
                skipped.append({"name":name,"ticker":symbol,"reason":reason,"days_available":len(prices)})
                print(f"✗ {reason}"); time.sleep(0.3); continue

            results.append({"name":name,"ticker":symbol,"price":round(float(prices.iloc[-1]),2),
                             "mom_3m":round(m3,2),"mom_6m":round(m6,2),"mom_12m":round(m12,2),
                             "compound_score":compound,
                             "market_cap_msek":round(mcap) if mcap else None,"fscore":fscore})
            print(f"✓  3M={round(m3,1):>7}%  6M={round(m6,1):>7}%  12M={round(m12,1):>7}%  COMPOUND={compound:>8}%")
        except Exception as e:
            skipped.append({"name":name,"ticker":symbol,"reason":f"Error: {str(e)[:60]}","days_available":0})
            print(f"✗ {str(e)[:50]}")
        time.sleep(0.3)

    results.sort(key=lambda x: x["compound_score"], reverse=True)
    for i, r in enumerate(results): r["rank"] = i+1

    top50 = results[:50]  # ← TOP 50
    prev_ranks = load_prev_ranks()
    for r in top50: r["prev_rank"] = prev_ranks.get(r["ticker"], None)
    save_prev_ranks(top50)

    print(f"\n{'='*65}\n  TOP 50 — COMPOUND MOMENTUM RANKING\n{'='*65}")
    for r in top50:
        prev = f"(prev #{r['prev_rank']})" if r['prev_rank'] else "(new)"
        print(f"  #{r['rank']:>2}  {r['name']:<30}  Score={r['compound_score']:>8}%  {prev}")

    output = {
        "updated": now.strftime("%Y-%m-%d %H:%M UTC"),
        "total_attempted": len(TICKERS),
        "stocks_screened": len(results),
        "skipped_count": len(skipped),
        "filters": {
            "size_filter": FILTER_BY_SIZE,
            "size_min_msek": MIN_MARKET_CAP_MSEK if FILTER_BY_SIZE else None,
            "fscore_filter": FILTER_BY_FSCORE,
            "fscore_min": MIN_FSCORE if FILTER_BY_FSCORE else None,
        },
        "top50": top50,   # ← key is top50
        "skipped": skipped,
    }
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n✅  Saved → {OUTPUT_JSON}  (top 50 stocks)")

if __name__ == "__main__":
    main()
