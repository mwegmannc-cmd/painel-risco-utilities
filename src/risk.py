"""Motor de risco: retorno do book, vol rolling, drawdown, tabelas por janela/ano/ativo."""
import numpy as np, pandas as pd
from config import *

ANN = 252

def book_returns(rets, cdi, longs, shorts, lg=LONG_GROSS, sg=SHORT_GROSS):
    """Rebalanceamento diário p/ pesos-alvo; caixa (1 - net) rende CDI. Sem custos/aluguel/impostos."""
    wl = {n: lg / len(longs) for n in longs}; ws = {n: -sg / len(shorts) for n in shorts}
    w = pd.Series({**wl, **ws}); r = rets[w.index].fillna(0)
    cash = 1 - w.sum()
    return (r * w).sum(axis=1) + cash * cdi.reindex(r.index).fillna(0)

def vol(r, win=None): return (r.iloc[-win:] if win else r).std() * np.sqrt(ANN)
def drawdown(r): c = (1 + r).cumprod(); return c / c.cummax() - 1
def sharpe(r, cdi):
    ex = r - cdi.reindex(r.index).fillna(0); return ex.mean() / ex.std() * np.sqrt(ANN)
def ann_ret(r): return (1 + r).prod() ** (ANN / len(r)) - 1

def window_table(series: dict):
    rows = {n: {**{f"{w}d": vol(s, w) for w in WINDOWS}, "Período": vol(s)} for n, s in series.items()}
    return pd.DataFrame(rows).T

def year_table(r):
    g = r.groupby(r.index.year)
    return pd.DataFrame({"vol": g.apply(vol), "maxdd": g.apply(lambda x: drawdown(x).min()),
                         "ret": g.apply(lambda x: (1 + x).prod() - 1)})

def stats(r, cdi):
    dd = drawdown(r)
    return {"ret_aa": ann_ret(r), "ret_acum": (1 + r).prod() - 1, "vol_atual_63d": vol(r, 63), "vol_media": vol(r),
            "maxdd": dd.min(), "dd_atual": dd.iloc[-1], "sharpe": sharpe(r, cdi)}
