# NSE NIFTY 500 STOCK LIST

url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers, timeout=30)
response.raise_for_status()

df = pd.read_csv(StringIO(response.text))

STOCKS = [
    symbol + ".NS"
    for symbol in df["Symbol"].dropna().astype(str).str.strip().unique()
]
