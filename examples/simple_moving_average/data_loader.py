"""
Data loader for NautilusTrader backtests.

Supports:
  - CSV files
  - Parquet files
  - HDF5 files
  - Yahoo Finance (yfinance)

Expected normalized columns:
  timestamp, open, high, low, close, volume
"""

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename and select required OHLCV columns."""
    df = df.copy()
    df.columns = [str(c).lower().strip() for c in df.columns]

    aliases = {
        "date": "timestamp",
        "datetime": "timestamp",
        "time": "timestamp",
    }
    df = df.rename(columns=aliases)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Got: {list(df.columns)}")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df[REQUIRED_COLUMNS].dropna()


def load_csv(path: str | Path) -> pd.DataFrame:
    """Load OHLCV data from a CSV file."""
    df = pd.read_csv(path)
    return normalize_columns(df)


def load_parquet(path: str | Path) -> pd.DataFrame:
    """Load OHLCV data from a Parquet file."""
    df = pd.read_parquet(path)
    return normalize_columns(df)


def load_hdf5(path: str | Path, key: str = "data") -> pd.DataFrame:
    """Load OHLCV data from an HDF5 file."""
    df = pd.read_hdf(path, key=key)
    return normalize_columns(df)


def fetch_yfinance(
    ticker: str = "SPY",
    start_date: str | None = None,
    end_date: str | None = None,
    period: str = "1y",
    interval: str = "1d",
    auto_adjust: bool = False,
) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance."""
    import yfinance as yf

    if start_date is not None:
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            auto_adjust=auto_adjust,
            progress=False,
        )
    else:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
            progress=False,
        )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Decide between Close and Adj Close
    if auto_adjust:
        if "Close" in df.columns and "Adj Close" in df.columns:
            df = df.drop(columns=["Close"])
        df = df.rename(columns={"Adj Close": "Close"})
    else:
        if "Adj Close" in df.columns:
            df = df.drop(columns=["Adj Close"])

    df = df.reset_index()
    return normalize_columns(df)


def load_data(data_config: dict) -> pd.DataFrame:
    """Dispatch to the correct loader based on config['source']."""
    source = data_config.get("source", "csv")

    if source == "csv":
        return load_csv(data_config["path"])

    if source == "parquet":
        return load_parquet(data_config["path"])

    if source == "hdf5":
        key = data_config.get("key", "data")
        return load_hdf5(data_config["path"], key=key)

    if source == "yfinance":
        return fetch_yfinance(
            ticker=data_config.get("ticker", "SPY"),
            start_date=data_config.get("start_date"),
            end_date=data_config.get("end_date"),
            period=data_config.get("period", "1y"),
            interval=data_config.get("interval", "1d"),
            auto_adjust=data_config.get("auto_adjust", False),
        )

    raise ValueError(f"Unsupported data source: {source}")