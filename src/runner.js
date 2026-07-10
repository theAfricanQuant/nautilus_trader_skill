const { spawn } = require('node:child_process');
const fs = require('node:fs/promises');
const path = require('node:path');
const { isUvProject } = require('./utils.js');

async function runBacktest(scriptPath, pythonExecutable = 'python', extraArgs = []) {
  const resolved = path.resolve(scriptPath);

  try {
    await fs.access(resolved);
  } catch (err) {
    console.error(`Error: backtest script not found at ${resolved}`);
    console.error(`Run 'nautilus-backtest init' to scaffold one.`);
    process.exit(1);
  }

  const cwd = path.dirname(resolved);
  const scriptName = path.basename(resolved);
  const useUv = await isUvProject(cwd);

  const command = useUv ? 'uv' : pythonExecutable;
  const args = useUv ? ['run', 'python', scriptName, ...extraArgs] : [scriptName, ...extraArgs];

  console.log(`Running backtest: ${command} ${args.join(' ')}`);
  console.log(`Working directory: ${cwd}`);
  if (useUv) {
    console.log('Detected uv project; using "uv run python".\n');
  }

  return new Promise((resolve, reject) => {
    const proc = spawn(command, args, {
      cwd,
      stdio: 'inherit',
      shell: false,
    });

    proc.on('error', (err) => {
      console.error(`Failed to start process: ${err.message}`);
      reject(err);
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        console.error(`Backtest exited with code ${code}`);
        process.exitCode = code ?? 1;
      }
      resolve();
    });
  });
}

module.exports = { runBacktest };