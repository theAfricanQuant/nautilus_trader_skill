# Licensing

This repository contains multiple pieces of software with different licenses. Using this package means you are bound by the terms of each relevant license.

## This package: `nautilus-trader-backtest`

The code in this repository — the Node.js CLI, project templates, example strategy, and data loaders — is released under the **MIT License**.

See [`LICENSE`](LICENSE) for the full text.

What this means for you:

- You may use this package for commercial or non-commercial purposes.
- You may modify, redistribute, and sublicense it.
- You do **not** have to open-source your own trading strategies or tools that use this package.
- You must include the MIT license and copyright notice when distributing this package itself.

## NautilusTrader

This package is a **harness** around [NautilusTrader](https://nautilustrader.io), which is the actual backtesting and trading engine.

NautilusTrader is developed by **Nautech Systems Pty Ltd** and is licensed under the **GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later)**.

- NautilusTrader source code: https://github.com/nautechsystems/nautilus_trader
- NautilusTrader license: https://github.com/nautechsystems/nautilus_trader/blob/develop/LICENSE

What this means for you:

- You may use NautilusTrader in commercial or proprietary applications.
- You may write proprietary trading strategies that run on top of NautilusTrader.
- If you **modify NautilusTrader itself**, you must share those modifications under the LGPL.
- You do **not** have to open-source your strategies, configurations, or this harness just because they use NautilusTrader.

## Third-party dependencies

Generated projects include dependencies such as:

- `pandas` — BSD-3-Clause
- `numpy` — BSD-3-Clause
- `yfinance` — Apache-2.0
- `tables` — BSD-3-Clause
- Other transitive dependencies resolved by `uv`

Each dependency has its own license. You can inspect them in the dependency metadata after running `uv sync`.

## Summary

| Component | License | Must share your own code? |
|---|---|---|
| This CLI harness | MIT | No |
| Your strategies and configs | Yours to choose | Up to you |
| NautilusTrader engine | LGPL-3.0-or-later | No, unless you modify NautilusTrader itself |
| Third-party Python packages | Various | Per-package terms |

If you have any doubt about how these licenses apply to your specific use case, consult a qualified legal professional.