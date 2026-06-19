import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const contract = JSON.parse(fs.readFileSync(new URL('../../ui/contract.json', import.meta.url), 'utf-8'));

test('UI contract declares health endpoint', () => {
  assert.equal(contract.appName, 'argo-workflows-demo-app');
  assert.ok(contract.publicRoutes.includes('/health'));
  assert.equal(contract.checks.requiresHealthEndpoint, true);
});

test('UI contract declares search support', () => {
  assert.ok(contract.publicRoutes.includes('/api/search'));
  assert.equal(contract.checks.supportsSearch, true);
});
