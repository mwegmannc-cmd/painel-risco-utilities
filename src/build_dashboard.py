"""Gera docs/index.html (autocontido, Chart.js via CDN). Uso: python src/build_dashboard.py [--demo]"""
import sys, json, numpy as np, pandas as pd
from config import *
from risk import *

DEMO = "--demo" in sys.argv

def demo_data():
    """SINTÉTICO — só p/ testar o código. Não representa nenhum resultado real."""
    rng = np.random.default_rng(0); idx = pd.bdate_range(START, "2026-09-30")
    names = list(YAHOO) + list(EUROPA_YAHOO) + list(BENCHMARKS)
    mkt = rng.normal(0, .008, len(idx))
    px = pd.DataFrame({n: 100 * np.exp(np.cumsum(.5 * mkt + rng.normal(0, .014, len(idx)))) for n in names}, index=idx)
    return px, pd.Series(.0005, index=idx, name="cdi")

def load():
    if DEMO: return demo_data()
    px = pd.read_csv("data/prices.csv", index_col=0, parse_dates=True)
    cdi = pd.read_csv("data/cdi.csv", index_col=0, parse_dates=True)["cdi"]
    return px, cdi

def series(s): return [None if pd.isna(x) else round(float(x), 5) for x in s]

def main():
    px, cdi = load(); rets = px.pct_change(); cdi = cdi.reindex(rets.index).fillna(0)
    br = book_returns(rets, cdi, LONGS_BR, SHORTS_BR)
    ibov = rets["Ibovespa"].fillna(0)
    eu_names = [n for n in EUROPA_YAHOO if n in rets and rets[n].notna().any()]
    eu = rets[eu_names].mean(axis=1).fillna(0) if eu_names else None
    ser = {"Book Brasil": br, "Ibovespa": ibov}
    if eu is not None: ser["Cesta Europa (proxy)"] = eu
    combo = None
    if EUROPA["long"] or EUROPA["short"]:
        e = book_returns(rets, cdi, EUROPA["long"], EUROPA["short"]); combo = 0.5 * br + 0.5 * e; ser["Book BR + Europa"] = combo
    focus = combo if combo is not None else br
    corr = {"BR x Ibov": br.corr(ibov)}
    if eu is not None: corr["BR x Europa"] = br.corr(eu); corr["Ibov x Europa"] = ibov.corr(eu)
    roll = {n: s.rolling(63).std() * np.sqrt(ANN) for n, s in ser.items()}
    cum = {n: (1 + s).cumprod() * 100 for n, s in ser.items()}
    dd = {n: drawdown(s) for n, s in ser.items()}
    per_asset = {n: vol(rets[n].dropna(), 252) for n in LONGS_BR + SHORTS_BR if n in rets}
    data = {"dates": [d.strftime("%Y-%m-%d") for d in br.index], "roll": {n: series(s) for n, s in roll.items()},
            "cum": {n: series(s) for n, s in cum.items()}, "dd": {n: series(s) for n, s in dd.items()},
            "stats": {n: stats(s, cdi) for n, s in ser.items()}, "windows": window_table(ser).to_dict("index"),
            "years": year_table(focus).round(4).to_dict("index"), "asset": per_asset, "corr": corr,
            "longs": LONGS_BR, "shorts": SHORTS_BR, "lg": LONG_GROSS, "sg": SHORT_GROSS, "demo": DEMO}
    html = TEMPLATE.replace("__DATA__", json.dumps(data, default=float))
    import os; os.makedirs("docs", exist_ok=True); open("docs/index.html", "w").write(html); print("docs/index.html ok")

TEMPLATE = r"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Painel de Risco — Regulados L/S</title><script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>:root{--bg:#fff;--fg:#1a1a1a;--mut:#666;--bd:#ddd;--c1:#1f6feb;--c2:#888;--c3:#e8590c}
@media(prefers-color-scheme:dark){:root{--bg:#121212;--fg:#eee;--mut:#999;--bd:#333;--c1:#58a6ff;--c2:#999;--c3:#ff8c42}}
body{background:var(--bg);color:var(--fg);font:14px system-ui;margin:0;padding:16px;max-width:1100px;margin:auto}
h1{font-size:20px}h2{font-size:15px;margin-top:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.k{border:1px solid var(--bd);border-radius:8px;padding:10px}.k b{display:block;font-size:20px}.k span{color:var(--mut);font-size:12px}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid var(--bd);padding:5px 8px;text-align:right}th:first-child,td:first-child{text-align:left}
.warn{background:#c92a2a;color:#fff;padding:8px;border-radius:6px;font-weight:600}.n{color:var(--mut);font-size:12px}canvas{max-height:300px}</style></head><body>
<div id=app></div><script>
const D=__DATA__,P=v=>v==null?'–':(v*100).toFixed(1)+'%',$=s=>document.getElementById(s);
const names=Object.keys(D.stats),main=names[names.length>2&&D.stats['Book BR + Europa']?names.indexOf('Book BR + Europa'):0],S=D.stats[main];
$('app').innerHTML=`<h1>Painel de Risco — Book Regulados (Utilities &amp; Infra)</h1>
${D.demo?'<div class=warn>DADOS SINTÉTICOS — apenas teste do código. Não usar como resultado.</div>':''}
<p class=n>Long: ${D.longs.join(', ')} (${P(D.lg)} do NAV) · Short: ${D.shorts.join(', ')} (${P(D.sg)}) · caixa a CDI · rebalanceamento diário · sem custos, aluguel ou impostos</p>
<div class=grid>${[['Retorno a.a.',P(S.ret_aa)],['Vol atual (63d)',P(S.vol_atual_63d)],['Vol média',P(S.vol_media)],['Max drawdown',P(S.maxdd)],['Drawdown atual',P(S.dd_atual)],['Sharpe (vs CDI)',S.sharpe.toFixed(2)]].map(([a,b])=>`<div class=k><span>${a}</span><b>${b}</b></div>`).join('')}</div>
<h2>Volatilidade anualizada por janela</h2><table><tr><th></th>${['21d','63d','126d','252d','Período'].map(x=>`<th>${x.replace('dd','d')}</th>`).join('')}</tr>${Object.entries(D.windows).map(([n,r])=>`<tr><td>${n}</td>${['21d','63d','126d','252d','Período'].map(k=>`<td>${P(r[k])}</td>`).join('')}</tr>`).join('')}</table>
<h2>Volatilidade rolling 63d</h2><canvas id=c1></canvas><h2>Drawdown</h2><canvas id=c2></canvas><h2>Retorno acumulado (base 100)</h2><canvas id=c3></canvas>
<h2>Correlação diária</h2><table>${Object.entries(D.corr).map(([k,v])=>`<tr><td>${k}</td><td>${v.toFixed(2)}</td></tr>`).join('')}</table>
<h2>Por ano (${main})</h2><table><tr><th>Ano</th><th>Vol</th><th>Max DD</th><th>Retorno</th></tr>${Object.entries(D.years).map(([y,r])=>`<tr><td>${y}</td><td>${P(r.vol)}</td><td>${P(r.maxdd)}</td><td>${P(r.ret)}</td></tr>`).join('')}</table>
<h2>Vol por ativo (252d)</h2><table>${Object.entries(D.asset).map(([n,v])=>`<tr><td>${n} ${D.shorts.includes(n)?'(short)':''}</td><td>${P(v)}</td></tr>`).join('')}</table>`;
const col=['#1f6feb','#888','#e8590c','#2b8a3e'];
const mk=(id,src,f)=>new Chart($(id),{type:'line',data:{labels:D.dates,datasets:Object.keys(src).map((n,i)=>({label:n,data:src[n],borderColor:col[i],borderWidth:1.3,pointRadius:0}))},options:{animation:false,scales:{x:{ticks:{maxTicksLimit:8}},y:{ticks:{callback:f}}},interaction:{mode:'index',intersect:false}}});
mk('c1',D.roll,v=>(v*100).toFixed(0)+'%');mk('c2',D.dd,v=>(v*100).toFixed(0)+'%');mk('c3',D.cum,v=>v.toFixed(0));
</script></body></html>"""

if __name__ == "__main__": main()
