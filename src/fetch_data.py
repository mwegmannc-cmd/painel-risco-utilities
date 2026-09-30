"""Baixa preços (Yahoo Finance) e CDI (BCB SGS 12) -> data/prices.csv, data/cdi.csv."""
import io, sys, requests, pandas as pd, yfinance as yf
from config import *

def main():
    tick = {**YAHOO, **EUROPA_YAHOO, **BENCHMARKS}
    px = yf.download(list(tick.values()), start=START, auto_adjust=True, progress=False)["Close"]
    px = px.rename(columns={v: k for k, v in tick.items()}).dropna(how="all")
    missing = [k for k in tick if k not in px or px[k].dropna().empty]
    if px.empty: sys.exit("Yahoo retornou vazio (rede bloqueada?)")
    px.to_csv("data/prices.csv"); print("prices", px.shape, "sem dados:", missing)
    d0 = pd.Timestamp(START).strftime("%d/%m/%Y")
    r = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados",
                     params={"formato": "json", "dataInicial": d0}, timeout=60); r.raise_for_status()
    cdi = pd.DataFrame(r.json()); cdi["data"] = pd.to_datetime(cdi["data"], dayfirst=True)
    cdi = cdi.set_index("data")["valor"].astype(float) / 100  # % a.d. -> decimal
    cdi.rename("cdi").to_csv("data/cdi.csv"); print("cdi", len(cdi))

if __name__ == "__main__": main()
