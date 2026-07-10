# Simple Moving Average Crossover Example

A minimal NautilusTrader backtest using an EMA crossover strategy.

## Run

```bash
# Sync dependencies
uv sync

# Generate sample data
uv run python scripts/generate_sample_data.py

# Run the backtest
uv run python run_backtest.py
```

Or from anywhere with the CLI harness:

```bash
cd examples/simple_moving_average
npx nautilus-trader-backtest run
```