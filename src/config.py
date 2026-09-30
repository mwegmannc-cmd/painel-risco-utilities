"""Configuração do book Regulados (Brasil + sleeve Europa). Pesos = premissas editáveis."""

# Nome -> ticker Yahoo Finance
YAHOO = {
    "Equatorial": "EQTL3.SA", "Eneva": "ENEV3.SA", "Copasa": "CSMG3.SA", "Orizon": "ORVR3.SA",
    "Cemig": "CMIG4.SA", "Sanepar": "SAPR11.SA", "Auren": "AURE3.SA",
    "Alupar": "ALUP11.SA", "Eletrobras (Axia)": "AXIA3.SA",  # AXIA3 = ex-ELET3; se faltar histórico, usar ELET3.SA
}
BENCHMARKS = {"Ibovespa": "^BVSP", "IDIV": "IDIV11.SA"}  # IDIV11 = ETF de dividendos (proxy p/ Utilities)

# Carteira Brasil. Peso = % do NAV. Premissa: pernas igualmente ponderadas; caixa remunerado a CDI.
LONGS_BR = ["Equatorial", "Eneva", "Copasa", "Orizon", "Cemig", "Sanepar", "Auren"]
SHORTS_BR = ["Alupar", "Eletrobras (Axia)"]
LONG_GROSS, SHORT_GROSS = 0.70, 0.20  # net = 50%

# Sleeve Europa: vazio até você definir os nomes. Ex.: {"long": ["Iberdrola"], "short": ["Uniper"]}
# Retornos em moeda local (sem hedge cambial) — limitação a resolver na próxima fase.
EUROPA = {"long": [], "short": []}
EUROPA_YAHOO = {  # universo da aba Regulados_Europa (usado p/ cesta proxy de correlação)
    "Iberdrola": "IBE.MC", "Endesa": "ELE.MC", "Enel": "ENEL.MI", "E.ON": "EOAN.DE", "RWE": "RWE.DE",
    "Redeia": "RED.MC", "Terna": "TRN.MI", "National Grid": "NG.L", "Snam": "SRG.MI",
    "United Utilities": "UU.L", "Severn Trent": "SVT.L", "Veolia": "VIE.PA", "SSE": "SSE.L",
    "Vinci": "DG.PA", "Aena": "AENA.MC", "Ferrovial": "FER.MC", "EDP": "EDP.LS", "Engie SA": "ENGI.PA",
}
START = "2021-05-01"
WINDOWS = [21, 63, 126, 252]
