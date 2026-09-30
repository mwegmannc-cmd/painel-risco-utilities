"""Lê o Excel do universo (abas Dados_* do Bloomberg) e salva preços em parquet/csv."""
import sys, openpyxl, pandas as pd

XLSX = "data/Universo_Long_x_Short_Regulados.xlsx"

def load_prices(wb, sheet):
    rows = list(wb[sheet].iter_rows(min_row=10, values_only=True))
    names, tickers, body = rows[0], rows[1], rows[4:]
    cols = [(i, names[i], tickers[i]) for i in range(3, len(names)) if names[i]]
    df = pd.DataFrame({n: [r[i] for r in body] for i, n, _ in cols},
                      index=pd.to_datetime([r[2] for r in body], errors="coerce"))
    df = df[df.index.notna()].apply(pd.to_numeric, errors="coerce").sort_index()
    tick = {n: t for _, n, t in cols}
    return df, tick

if __name__ == "__main__":
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    for s in ["Dados_Latam", "Dados_Europa"]:
        df, tick = load_prices(wb, s)
        print(s, df.shape, df.index.min().date(), df.index.max().date())
        info = pd.DataFrame({"ticker": pd.Series(tick), "n": df.count(),
            "first": df.apply(lambda c: c.first_valid_index()), "last": df.apply(lambda c: c.last_valid_index())})
        print(info.to_string())
