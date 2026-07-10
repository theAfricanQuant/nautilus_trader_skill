const { spawn } = require('node:child_process');
const fs = require('node:fs/promises');
const path = require('node:path');

function exec(command, args, options = {}) {
  return new Promise((resolve) => {
    const proc = spawn(command, args, { stdio: 'pipe', ...options });
    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('error', (err) => {
      resolve({ code: -1, stdout: '', stderr: err.message });
    });

    proc.on('close', (code) => {
      resolve({ code, stdout: stdout.trim(), stderr: stderr.trim() });
    });
  });
}

async function hasUv() {
  const result = await exec('uv', ['--version']);
  return result.code === 0;
}

async function isUvProject(dir) {
  try {
    await fs.access(path.join(dir, 'pyproject.toml'));
    return true;
  } catch {
    return false;
  }
}

async function checkEnvironment(cwd = process.cwd()) {
  console.log('Checking uv / Python environment\n');

  let ok = true;
  const inUvProject = await isUvProject(cwd);

  // uv
  const uvResult = await exec('uv', ['--version']);
  if (uvResult.code !== 0) {
    console.error('❌ uv is not installed or not on PATH.');
    console.error('   Install it: https://docs.astral.sh/uv/getting-started/installation/');
    return false;
  }
  console.log(`✅ uv: ${uvResult.stdout}`);

  // Python via uv
  const pyResult = await exec('uv', ['run', 'python', '--version'], { cwd });
  if (pyResult.code !== 0) {
    console.error('❌ Could not run Python through uv.');
    console.error(`   ${pyResult.stderr}`);
    ok = false;
  } else {
    console.log(`✅ Python (via uv): ${pyResult.stdout || pyResult.stderr}`);
  }

  if (inUvProject) {
    console.log('\nDetected uv project (pyproject.toml). Checking dependencies...');

    // nautilus_trader import
    const ntResult = await exec('uv', ['run', 'python', '-c', 'import nautilus_trader; print(nautilus_trader.__version__)'], { cwd });
    if (ntResult.code !== 0) {
      console.error('❌ nautilus_trader is not available in this uv project.');
      console.error(`   ${ntResult.stderr}`);
      console.error('   Add it: uv add nautilus_trader');
      ok = false;
    } else {
      console.log(`✅ nautilus_trader: ${ntResult.stdout}`);
    }

    // pandas import
    const pdResult = await exec('uv', ['run', 'python', '-c', 'import pandas; print(pandas.__version__)'], { cwd });
    if (pdResult.code !== 0) {
      console.warn('⚠️  pandas is not available. Generated projects use pandas for CSV loading.');
      console.warn('   Add it: uv add pandas');
    } else {
      console.log(`✅ pandas: ${pdResult.stdout}`);
    }
  } else {
    console.log('\nNo uv project (pyproject.toml) in current directory.');
    console.log('   Run this command inside a generated project to verify NautilusTrader dependencies.');
    console.log('   Dependencies will be installed automatically on first `uv run`.');
  }

  console.log(ok ? '\nEnvironment looks good.' : '\nEnvironment has issues. Fix them before running backtests.');
  return ok;
}

module.exports = { exec, hasUv, isUvProject, checkEnvironment };