# painel-risco-utilities
Painel de risco (vol e drawdown) do book **Regulados (Utilities & Infra)** long/short: Brasil + sleeve Europa.
Inspirado no painel de risco da carteira geral do fundo.

## Uso
```
pip install -r requirements.txt
python src/fetch_data.py        # Yahoo Finance + CDI (BCB SGS 12) -> data/*.csv  (precisa de internet)
python src/build_dashboard.py   # gera docs/index.html
python src/build_dashboard.py --demo   # dados SINTÉTICOS, só p/ testar o código
```
- `src/config.py`: tickers, pernas long/short, pesos (premissa: 70% long / 20% short igualmente ponderados, caixa a CDI) e sleeve Europa.
- `src/risk.py`: vol rolling (21/63/126/252d), drawdown, Sharpe, tabelas por ano e por ativo.
- `data/Universo_Long_x_Short_Regulados.xlsx`: universo. **Atenção:** as abas `Dados_*` (Bloomberg) estão sem cache (`#NAME?`); por isso os preços vêm do Yahoo.

## Limitações atuais
Sem custos, aluguel, impostos; Europa em moeda local (sem câmbio); nomes do sleeve Europa ainda não definidos (`EUROPA` em config vazio).
