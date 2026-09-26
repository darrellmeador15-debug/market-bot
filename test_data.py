from data_loader import load_data


if __name__ == "__main__":
    data = load_data("AAPL", period="1mo", interval="1d")

    print("Market data loaded successfully.")
    print(f"Rows: {len(data)}")
    print(data.tail())
