const fs = require('node:fs/promises');
const path = require('node:path');
const { getTemplate } = require('./templates.js');

const TEMPLATE_FILES = [
  { src: 'pyproject.toml.template', dest: 'pyproject.toml' },
  { src: 'project_readme.md.template', dest: 'README.md' },
  { src: 'config.json.template', dest: 'config.json' },
  { src: 'data_loader.py.template', dest: 'data_loader.py' },
  { src: 'run_backtest.py.template', dest: 'run_backtest.py' },
  { src: 'generate_sample_data.py.template', dest: 'scripts/generate_sample_data.py' },
];

async function createProject(targetDir, templateName = 'ema-cross') {
  try {
    await fs.access(targetDir);
    console.error(`Error: directory already exists: ${targetDir}`);
    process.exit(1);
  } catch {
    // directory does not exist, continue
  }

  await fs.mkdir(targetDir, { recursive: true });
  await fs.mkdir(path.join(targetDir, 'data'), { recursive: true });
  await fs.mkdir(path.join(targetDir, 'scripts'), { recursive: true });
  await fs.mkdir(path.join(targetDir, 'results'), { recursive: true });

  const templatesDir = path.join(__dirname, 'templates');
  const projectName = path.basename(targetDir);

  for (const { src, dest } of TEMPLATE_FILES) {
    const srcPath = path.join(templatesDir, src);
    const destPath = path.join(targetDir, dest);
    let content = await fs.readFile(srcPath, 'utf-8');

    content = content.replace(/\{\{project_name\}\}/g, projectName);
    content = content.replace(/\{\{strategy_template\}\}/g, templateName);

    await fs.mkdir(path.dirname(destPath), { recursive: true });
    await fs.writeFile(destPath, content);
  }

  const strategyContent = getTemplate(templateName);
  await fs.writeFile(path.join(targetDir, 'strategy.py'), strategyContent);

  console.log(`Created uv-managed backtest project at ${targetDir}`);
  console.log(`\nNext steps:`);
  console.log(`  cd ${projectName}`);
  console.log(`  uv sync`);
  console.log(`  uv run python scripts/generate_sample_data.py`);
  console.log(`  npx nautilus-trader-backtest run`);
}

module.exports = { createProject };