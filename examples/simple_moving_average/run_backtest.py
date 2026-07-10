"""
Run the EMA crossover backtest.
"""

import json
from decimal import Decimal
from pathlib import Path

from data_loader import load_data

from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.model.currencies import Currency
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import InstrumentId, Symbol, TraderId, Venue
from nautilus_trader.model.instruments import CurrencyPair, Equity
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
    instrument_type = instrument_cfg.get("type", "CurrencyPair")

    if instrument_type == "CurrencyPair":
        from nautilus_trader.model.currencies import Currency as Ccy
        base = Ccy.from_str(instrument_cfg["base_currency"])
        quote = Ccy.from_str(instrument_cfg["quote_currency"])
        price_precision = instrument_cfg["price_precision"]
        size_precision = instrument_cfg.get("size_precision", 0)

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

    if instrument_type == "Equity":
        currency = Currency.from_str(instrument_cfg.get("currency", "USD"))
        price_precision = instrument_cfg["price_precision"]
        lot_size = Quantity.from_str(str(instrument_cfg.get("lot_size", "1")))

        return Equity(
            instrument_id=instrument_id,
            raw_symbol=Symbol(instrument_cfg.get("symbol", instrument_id.symbol.value)),
            currency=currency,
            price_precision=price_precision,
            price_increment=Price.from_str(precision_increment(price_precision)),
            lot_size=lot_size,
            maker_fee=Decimal("0.0001"),
            taker_fee=Decimal("0.0001"),
            ts_event=0,
            ts_init=0,
        )

    raise ValueError(f"Unsupported instrument type: {instrument_type}")


def load_bars(config, bar_type):
    df = load_data(config["data"])

    price_precision = config["instrument"]["price_precision"]
    size_precision = config["instrument"].get("size_precision", 0)

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
    params["trade_size"] = Quantity.from_str(str(params["trade_size"]))

    return strategy_class(config_class(**params))


def main():
    config = load_config()

    bar_type = BarType.from_str(config["bar_type"])
    venue = Venue(config["venue"]["name"])
    base_currency = Currency.from_str(config["venue"].get("base_currency", "USD"))

    engine = BacktestEngine(
        config=BacktestEngineConfig(trader_id=TraderId(config["trader_id"]))
    )

    engine.add_venue(
        venue=venue,
        oms_type=OmsType[config["venue"]["oms_type"]],
        account_type=AccountType[config["venue"]["account_type"]],
        base_currency=base_currency,
        starting_balances=[Money(config["venue"]["starting_balance"], base_currency)],
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