# NautilusTrader Backtest Harness

A small, `npx`-installable CLI harness that scaffolds and runs [NautilusTrader](https://nautilustrader.io) backtests. It does not replace NautilusTrader — it wraps the Python backtest workflow so you can generate a project, check your environment, and run a backtest from the terminal with one command.

This package assumes you use [`uv`](https://docs.astral.sh/uv/) for Python environment management. No `pip` commands are used.

## Install / run with npx

No global install required:

```bash
npx nautilus-trader-backtest --help
```

Or alias:

```bash
npx ntb --help
```

If you want it in your project:

```bash
npm install nautilus-trader-backtest
```

## Prerequisites

- Node.js 18+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed and on your PATH

## Quick start

```bash
# 1. Scaffold a backtest project
npx nautilus-trader-backtest init my-strategy

# 2. Move into it
cd my-strategy

# 3. Generate synthetic sample data
uv run python scripts/generate_sample_data.py

# 4. Run the backtest
npx nautilus-trader-backtest run
```

The CLI automatically detects a `pyproject.toml` and runs the backtest with `uv run python`.

## CLI commands

### `init [project-name]`

Creates a new backtest project folder with:

```
my-strategy/
├── pyproject.toml              # uv project file with deps
├── README.md                   # Project-specific readme
├── config.json                 # Backtest configuration
├── strategy.py                 # Your strategy implementation
├── run_backtest.py             # Python entry point
├── scripts/
│   └── generate_sample_data.py # Makes a sample CSV of OHLCV bars
├── data/
└── results/
```

Example:

```bash
npx nautilus-trader-backtest init my-strategy
```

### `run [script-path]`

Runs a backtest. Defaults to `run_backtest.py` in the current directory.

```bash
npx nautilus-trader-backtest run
npx nautilus-trader-backtest run ./run_backtest.py
```

You can also pass extra arguments through to the Python script:

```bash
npx nautilus-trader-backtest run -- --verbose
```

If the working directory contains a `pyproject.toml`, the harness invokes `uv run python <script>`. Otherwise it falls back to plain `python`.

### `check`

Checks that `uv`, Python, and `nautilus_trader` are available.

```bash
npx nautilus-trader-backtest check
```

### `template [name]`

Prints a built-in strategy template to stdout. Useful for piping into a new file:

```bash
npx nautilus-trader-backtest template ema-cross > strategy.py
```

## How it works

1. The CLI is written in Node.js so it can be distributed via npm and invoked with `npx`.
2. The actual backtest still runs in Python — NautilusTrader is the engine.
3. The generated `run_backtest.py` loads `config.json`, builds a `BacktestEngine`, and imports the strategy class from `strategy.py`.
4. `uv` manages the Python environment and dependencies automatically via `pyproject.toml`.

## Generated project structure

### `pyproject.toml`

```toml
[project]
name = "my-strategy"
version = "0.1.0"
description = "NautilusTrader backtest project"
requires-python = ">=3.10"
dependencies = [
    "nautilus_trader",
    "pandas",
    "numpy",
]
```

### `config.json`

```json
{
  "trader_id": "BACKTESTER-001",
  "instrument": {
    "id": "EURUSD.SIM",
    "type": "CurrencyPair",
    "base_currency": "EUR",
    "quote_currency": "USD",
    "price_precision": 5,
    "size_precision": 0
  },
  "bar_type": "EURUSD.SIM-1-MINUTE-LAST-EXTERNAL",
  "venue": {
    "name": "SIM",
    "oms_type": "NETTING",
    "account_type": "MARGIN",
    "starting_balance": 100000
  },
  "data": {
    "path": "data/sample_data.csv"
  },
  "strategy": {
    "path": "strategy.py",
    "class_name": "EMACross",
    "config_class_name": "EMACrossConfig",
    "params": {
      "fast_period": 10,
      "slow_period": 20,
      "trade_size": "1000"
    }
  }
}
```

### `strategy.py`

Generated from the built-in EMA-crossover template. You can replace it with any NautilusTrader strategy.

### `run_backtest.py`

The Python harness that wires config → engine → strategy → results.

## Example

See the [`examples/simple_moving_average`](examples/simple_moving_average) directory for a ready-to-adapt project.

## Development

```bash
# Clone / open this package
cd nautilus_trader_skill

# Install Node dependencies
npm install

# Run tests
npm test

# Link locally for testing
npm link
nautilus-backtest --help
```

## Publishing

```bash
npm version patch
npm publish
```

After publishing, anyone can run:

```bash
npx nautilus-trader-backtest init my-strategy
```

## License

MIT