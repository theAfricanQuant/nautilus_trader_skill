"""
Run the EMA crossover backtest.
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd

from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import InstrumentId, TraderId, Venue
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Money, Price, Quantity

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def precision_increment(precision: int) -> str:
    """Return a string representing one increment at the given precision."""
    if precision <= 0:
        return "1"
    return "0." + "0" * (precision - 1) + "1"


def make_instrument(config):
    instrument_cfg = config["instrument"]
    instrument_id = InstrumentId.from_str(instrument_cfg["id"])

    from nautilus_trader.model.currencies import Currency
    from nautilus_trader.model.identifiers import Symbol

    base = Currency.from_str(instrument_cfg["base_currency"])
    quote = Currency.from_str(instrument_cfg["quote_currency"])
    price_precision = instrument_cfg["price_precision"]
    size_precision = instrument_cfg["size_precision"]

    return CurrencyPair(
        instrument_id=instrument_id,
        raw_symbol=Symbol(instrument_id.symbol.value),
        base_currency=base,
        quote_currency=quote,
        price_precision=price_precision,
        size_precision=size_precision,
        price_increment=Price.from_str(precision_increment(price_precision)),
        size_increment=Quantity.from_str(precision_increment(size_precision)),
        maker_fee=Decimal("0.0001"),
        taker_fee=Decimal("0.0001"),
        ts_event=0,
        ts_init=0,
    )


def load_bars(config, bar_type):
    data_path = Path(config["data"]["path"])
    if not data_path.is_absolute():
        data_path = Path(__file__).parent / data_path

    if not data_path.exists():
        print(f"Data file not found: {data_path}")
        print("Generate sample data with: python scripts/generate_sample_data.py")
        sys.exit(1)

    price_precision = config["instrument"]["price_precision"]
    size_precision = config["instrument"]["size_precision"]

    df = pd.read_csv(data_path, parse_dates=["timestamp"])
    bars = []
    for _, row in df.iterrows():
        ts = int(row["timestamp"].timestamp() * 1e9)
        bars.append(
            Bar(
                bar_type=bar_type,
                open=Price.from_str(f"{row['open']:.{price_precision}f}"),
                high=Price.from_str(f"{row['high']:.{price_precision}f}"),
                low=Price.from_str(f"{row['low']:.{price_precision}f}"),
                close=Price.from_str(f"{row['close']:.{price_precision}f}"),
                volume=Quantity.from_str(f"{row['volume']:.{size_precision}f}"),
                ts_event=ts,
                ts_init=ts,
            )
        )
    return bars


def load_strategy(config):
    strategy_cfg = config["strategy"]
    strategy_path = Path(strategy_cfg["path"])
    if not strategy_path.is_absolute():
        strategy_path = Path(__file__).parent / strategy_path

    import importlib.util

    spec = importlib.util.spec_from_file_location("strategy", strategy_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    strategy_class = getattr(module, strategy_cfg["class_name"])
    config_class = getattr(module, strategy_cfg["config_class_name"])

    params = dict(strategy_cfg["params"])
    params["instrument_id"] = config["instrument"]["id"]
    params["bar_type"] = config["bar_type"]
    params["trade_size"] = Decimal(params["trade_size"])

    return strategy_class(config_class(**params))


def main():
    config = load_config()

    bar_type = BarType.from_str(config["bar_type"])
    venue = Venue(config["venue"]["name"])

    engine = BacktestEngine(
        config=BacktestEngineConfig(trader_id=TraderId(config["trader_id"]))
    )

    engine.add_venue(
        venue=venue,
        oms_type=OmsType[config["venue"]["oms_type"]],
        account_type=AccountType[config["venue"]["account_type"]],
        base_currency=USD,
        starting_balances=[Money(config["venue"]["starting_balance"], USD)],
    )

    instrument = make_instrument(config)
    engine.add_instrument(instrument)

    bars = load_bars(config, bar_type)
    engine.add_data(bars)

    strategy = load_strategy(config)
    engine.add_strategy(strategy)

    print(f"Running backtest with {len(bars)} bars...")
    engine.run()

    print("\n=== Account Report ===")
    print(engine.trader.generate_account_report(venue))

    print("\n=== Order Fills ===")
    print(engine.trader.generate_order_fills_report())

    print("\n=== Positions ===")
    print(engine.trader.generate_positions_report())


if __name__ == "__main__":
    main()