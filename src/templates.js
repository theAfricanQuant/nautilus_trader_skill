const fs = require('node:fs');
const path = require('node:path');

const TEMPLATES_DIR = path.join(__dirname, 'templates');

const TEMPLATE_MAP = {
  'ema-cross': 'strategy_ema_cross.py.template',
  'empty': 'strategy_empty.py.template',
};

function listTemplates() {
  return Object.keys(TEMPLATE_MAP);
}

function getTemplate(name) {
  const fileName = TEMPLATE_MAP[name];
  if (!fileName) {
    throw new Error(`Unknown template "${name}". Available: ${listTemplates().join(', ')}`);
  }
  return fs.readFileSync(path.join(TEMPLATES_DIR, fileName), 'utf-8');
}

module.exports = { listTemplates, getTemplate };