import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
const source = readFileSync(process.argv[2], 'utf8')
const expression = source.match(/return (Object.values\(xoasInfo.value\).reduce[\s\S]*?)\n\}\)/)[1]
const select = new Function('xoasInfo', 'return ' + expression.replace('<ClientInfo | undefined>', ''))
assert.equal(select({ value: {} }), undefined)
const old = { lastConnected: 1 }, latest = { lastConnected: 2 }
assert.equal(select({ value: { old } }), old)
assert.equal(select({ value: { latest, old } }), latest)
assert.equal(select({ value: { old, latest } }), latest)
console.log('XoaButton empty and non-empty selection passed')
