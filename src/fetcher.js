const { spawn } = require('node:child_process');
const fs = require('node:fs/promises');
const path = require('node:path');
const { isUvProject } = require('./utils.js');

async function fetchData(options) {
  const cwd = process.cwd();
  const useUv = await isUvProject(cwd);

  if (!useUv) {
    console.error('Error: no uv project (pyproject.toml) found in current directory.');
    console.error('Run `nautilus-backtest init` first.');
    process.exit(1);
  }

  const outputPath = path.resolve(options.output);
  const outputDir = path.dirname(outputPath);
  await fs.mkdir(outputDir, { recursive: true });

  const pythonScript = `
import json
from pathlib import Path
from data_loader import fetch_yfinance
import pandas as pd

df = fetch_yfinance(
    ticker=${JSON.stringify(options.ticker)},
    start_date=${options.startDate ? JSON.stringify(options.startDate) : 'None'},
    end_date=${options.endDate ? JSON.stringify(options.endDate) : 'None'},
    period=${JSON.stringify(options.period)},
    interval=${JSON.stringify(options.interval)},
    auto_adjust=${options.autoAdjust ? 'True' : 'False'},
)

output_path = Path(${JSON.stringify(outputPath)})
if output_path.suffix == '.csv':
    df.to_csv(output_path, index=False)
elif output_path.suffix == '.parquet':
    df.to_parquet(output_path, index=False)
elif output_path.suffix in ('.h5', '.hdf5'):
    df.to_hdf(output_path, key='data', mode='w')
else:
    raise ValueError(f"Unsupported output format: {output_path.suffix}")

print(f"Downloaded {len(df)} rows from {df['timestamp'].min()} to {df['timestamp'].max()}")
print(f"Saved to {output_path}")
`;

  const command = useUv ? 'uv' : 'python';
  const args = useUv ? ['run', 'python', '-c', pythonScript] : ['-c', pythonScript];

  console.log(`Fetching ${options.ticker} from Yahoo Finance...`);
  console.log(`Output: ${outputPath}`);

  return new Promise((resolve, reject) => {
    const proc = spawn(command, args, {
      cwd,
      stdio: 'inherit',
      shell: false,
    });

    proc.on('error', (err) => {
      console.error(`Failed to start fetch: ${err.message}`);
      reject(err);
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        console.error(`Fetch exited with code ${code}`);
        process.exitCode = code ?? 1;
      }
      resolve();
    });
  });
}

module.exports = { fetchData };