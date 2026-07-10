# NautilusTrader Backtest Harness

A small, `npx`-installable CLI harness that scaffolds and runs [NautilusTrader](https://nautilustrader.io) backtests. It does not replace NautilusTrader — it wraps the Python backtest workflow so you can generate a project, fetch data, and run a backtest from the terminal with one command.

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

# 3. Fetch market data from Yahoo Finance
npx nautilus-trader-backtest fetch-data --ticker SPY --period 1y --output data/market_data.csv

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
├── data_loader.py              # CSV / Parquet / HDF5 / yfinance loaders
├── strategy.py                 # Your strategy implementation
├── run_backtest.py             # Python entry point
├── scripts/
│   └── generate_sample_data.py # Makes synthetic OHLCV bars
├── data/                       # Drop your market data here
└── results/
```

Example:

```bash
npx nautilus-trader-backtest init my-strategy
```

### `fetch-data`

Downloads OHLCV data from Yahoo Finance into `data/`.

```bash
npx nautilus-trader-backtest fetch-data --ticker SPY --period 1y --output data/market_data.csv
npx nautilus-trader-backtest fetch-data --ticker BTC-USD --interval 1h --output data/btc.csv
npx nautilus-trader-backtest fetch-data --ticker AAPL --start-date 2023-01-01 --end-date 2024-01-01 --output data/aapl.parquet
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

## Data sources

The generated `data_loader.py` supports:

- **CSV** — `data.source: "csv"`
- **Parquet** — `data.source: "parquet"`
- **HDF5** — `data.source: "hdf5"`
- **Yahoo Finance** — `data.source: "yfinance"`

### Using your own CSV

1. Drop `your_data.csv` into `my-strategy/data/`.
2. Update `config.json`:

```json
"data": {
  "source": "csv",
  "path": "data/your_data.csv"
}
```

Your CSV must have columns: `timestamp`, `open`, `high`, `low`, `close`, `volume`.

### Using yfinance

The default generated project uses yfinance. Set it in `config.json`:

```json
"data": {
  "source": "yfinance",
  "ticker": "SPY",
  "period": "1y",
  "interval": "1d",
  "auto_adjust": false
}
```

Then either run `fetch-data` to save the file, or just run `npx nautilus-trader-backtest run` — `run_backtest.py` will download it on the fly.

## Instrument types

The generated `run_backtest.py` supports:

- `CurrencyPair` (e.g. `EURUSD.SIM`)
- `Equity` (e.g. `SPY.SIM`)

Configure the instrument in `config.json`. The venue in the instrument ID must match the venue configured below it:

```json
"instrument": {
  "id": "SPY.SIM",
  "type": "Equity",
  "symbol": "SPY",
  "venue": "SIM",
  "currency": "USD",
  "price_precision": 2,
  "lot_size": "1"
},
"venue": {
  "name": "SIM",
  ...
}
```

## How it works

1. The CLI is written in Node.js so it can be distributed via npm and invoked with `npx`.
2. The actual backtest still runs in Python — NautilusTrader is the engine.
3. The generated `run_backtest.py` loads `config.json`, builds a `BacktestEngine`, and imports the strategy class from `strategy.py`.
4. `uv` manages the Python environment and dependencies automatically via `pyproject.toml`.
5. `data_loader.py` abstracts data ingestion so you can swap CSV, Parquet, HDF5, or Yahoo Finance without touching the backtest wiring.

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

This CLI harness is licensed under the MIT License — see [`LICENSE`](LICENSE).

This package builds on [NautilusTrader](https://nautilustrader.io), which is licensed under LGPL-3.0-or-later by Nautech Systems Pty Ltd. For a full licensing breakdown, see [`LICENSES.md`](LICENSES.md).