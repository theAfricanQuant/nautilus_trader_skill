const { Command } = require('commander');
const path = require('node:path');
const { createProject } = require('./project.js');
const { runBacktest } = require('./runner.js');
const { checkEnvironment } = require('./utils.js');
const { getTemplate, listTemplates } = require('./templates.js');

function createCli() {
  const program = new Command();

  program
    .name('nautilus-backtest')
    .description('CLI harness for NautilusTrader backtests')
    .version(require('../package.json').version);

  program
    .command('init [project-name]')
    .description('Scaffold a new uv-managed backtest project')
    .option('-t, --template <name>', 'strategy template to use', 'ema-cross')
    .action(async (projectName, options) => {
      const targetDir = path.resolve(projectName || 'nautilus-backtest-project');
      await createProject(targetDir, options.template);
    });

  program
    .command('run [script-path]')
    .description('Run a backtest Python script (default: ./run_backtest.py)')
    .option('-p, --python <executable>', 'Python executable to use when not in a uv project', 'python')
    .allowUnknownOption()
    .action(async (scriptPath, options, command) => {
      const target = path.resolve(scriptPath || 'run_backtest.py');
      const extraArgs = command.args.slice(1);
      await runBacktest(target, options.python, extraArgs);
    });

  program
    .command('check')
    .description('Check uv, Python, and NautilusTrader availability')
    .action(async () => {
      const ok = await checkEnvironment();
      process.exit(ok ? 0 : 1);
    });

  program
    .command('template [name]')
    .description('Print a strategy template to stdout')
    .action((name) => {
      if (!name) {
        console.log('Available templates:');
        for (const t of listTemplates()) {
          console.log(`  - ${t}`);
        }
        return;
      }
      console.log(getTemplate(name));
    });

  return program;
}

async function run(argv) {
  const program = createCli();
  await program.parseAsync(argv);
}

module.exports = { createCli, run };