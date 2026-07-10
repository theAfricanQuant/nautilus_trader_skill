"""
EMA Crossover strategy for NautilusTrader.
"""

from decimal import Decimal

from nautilus_trader.config import StrategyConfig
from nautilus_trader.indicators.averages import ExponentialMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.strategy import Strategy


class EMACrossConfig(StrategyConfig):
    instrument_id: str
    bar_type: str
    trade_size: Decimal
    fast_period: int = 10
    slow_period: int = 20


class EMACross(Strategy):
    def __init__(self, config: EMACrossConfig):
        super().__init__(config)
        self._instrument_id_str = config.instrument_id
        self._bar_type_str = config.bar_type
        self._trade_size = (
            config.trade_size
            if isinstance(config.trade_size, Quantity)
            else Quantity.from_str(str(config.trade_size))
        )
        self._fast_period = config.fast_period
        self._slow_period = config.slow_period

        self._bar_type = None
        self._instrument_id = None
        self._fast_ema = ExponentialMovingAverage(self._fast_period)
        self._slow_ema = ExponentialMovingAverage(self._slow_period)
        self._prev_fast = None
        self._prev_slow = None

    def on_start(self):
        from nautilus_trader.model.data import BarType
        from nautilus_trader.model.identifiers import InstrumentId

        self._instrument_id = InstrumentId.from_str(self._instrument_id_str)
        self._bar_type = BarType.from_str(self._bar_type_str)
        self.subscribe_bars(self._bar_type)

    def on_bar(self, bar: Bar):
        self._fast_ema.update_raw(bar.close.as_double())
        self._slow_ema.update_raw(bar.close.as_double())

        fast_val = self._fast_ema.value
        slow_val = self._slow_ema.value

        if fast_val is None or slow_val is None:
            return

        if self._prev_fast is not None:
            was_below = self._prev_fast <= self._prev_slow
            is_above = fast_val > slow_val
            was_above = self._prev_fast >= self._prev_slow
            is_below = fast_val < slow_val

            positions = self.cache.positions(instrument_id=self._instrument_id)
            is_flat = not positions or not any(p.is_open for p in positions)

            if was_below and is_above and is_flat:
                order = self.order_factory.market(
                    instrument_id=self._instrument_id,
                    order_side=OrderSide.BUY,
                    quantity=self._trade_size,
                )
                self.submit_order(order)
            elif was_above and is_below and not is_flat:
                order = self.order_factory.market(
                    instrument_id=self._instrument_id,
                    order_side=OrderSide.SELL,
                    quantity=self._trade_size,
                )
                self.submit_order(order)

        self._prev_fast = fast_val
        self._prev_slow = slow_val

    def on_stop(self):
        pass