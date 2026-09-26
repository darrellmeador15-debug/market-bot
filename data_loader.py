import yfinance as yf


def load_data(ticker, period="2y", interval="1d"):
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise ValueError(f"No market data returned for {ticker}")

    data = data.reset_index()

    if "Datetime" in data.columns:
        data = data.rename(columns={"Datetime": "timestamp"})
    elif "Date" in data.columns:
        data = data.rename(columns={"Date": "timestamp"})

    data.columns = [
        str(column).lower().replace(" ", "_")
        for column in data.columns
    ]

    return data
