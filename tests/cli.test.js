const assert = require('node:assert');
const { describe, it } = require('node:test');
const { createCli } = require('../src/cli.js');
const { getTemplate, listTemplates } = require('../src/templates.js');

describe('CLI', () => {
  it('should create a commander program with expected commands', () => {
    const program = createCli();
    const names = program.commands.map((c) => c.name());
    assert.deepStrictEqual(names.sort(), ['check', 'fetch-data', 'init', 'run', 'template']);
  });
});

describe('Templates', () => {
  it('should list built-in templates', () => {
    const templates = listTemplates();
    assert.ok(templates.includes('ema-cross'));
    assert.ok(templates.includes('empty'));
  });

  it('should return the EMA crossover template', () => {
    const content = getTemplate('ema-cross');
    assert.ok(content.includes('class EMACross'));
    assert.ok(content.includes('class EMACrossConfig'));
  });

  it('should throw for unknown templates', () => {
    assert.throws(() => getTemplate('nonexistent'), /Unknown template/);
  });
});