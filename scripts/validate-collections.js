#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const assert = require('node:assert/strict');
const pass = JSON.parse(fs.readFileSync('lab05-collection.json', 'utf8'));
const fail = JSON.parse(fs.readFileSync('lab05-collection-fail.json', 'utf8'));
function collect(items, out = []) {
  for (const item of items) {
    for (const event of item.event || []) if (event.listen === 'test') out.push(...event.script.exec);
    if (item.item) collect(item.item, out);
  }
  return out;
}
assert.equal(pass.item.length, 13);
assert.equal(fail.item.length, 13);
for (const collection of [pass, fail]) {
  for (let i = 0; i < 12; i += 1) {
    const folder = collection.item[i];
    const post = folder.item[folder.item.length - 1];
    assert.equal(post.request.method, 'POST');
    assert.equal(post.request.url.raw, '{{baseUrl}}/registrations');
    for (const setup of folder.item.slice(0, -1)) {
      assert.equal(setup.request.method, 'PUT');
      assert.ok(setup.request.url.raw.startsWith('{{baseUrl}}/'));
    }
  }
  assert.equal(collection.item[11].item[0].request.url.raw, 'https://jsonplaceholder.typicode.com/users');
}
assert.equal(collect(pass.item).length, 27);
assert.equal(collect(fail.item).length, 27);
const restored = JSON.parse(JSON.stringify(fail));
restored.info.name = pass.info.name;
const last = restored.item[0].item.at(-1);
last.event[0].script.exec[0] = pass.item[0].item.at(-1).event[0].script.exec[0];
assert.deepEqual(restored, pass);
console.log('Collection validation: 13 folders, 27 assertions; fail fixture differs by one status oracle only.');
