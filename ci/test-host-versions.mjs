import assert from 'node:assert/strict'
import test from 'node:test'
import { readHostVersions } from '../patches/host-versions/hl-host-versions.ts'

test('installed versions come from plugin fields, not release/source guesses', async () => {
  const value = { 'xcp-hl-release': '1.0-9', 'xo-lite-ce': '0.21.0-27.gfixture', 'xoa-proxy': '0.1.3-18', iso: 'ce56', foreign: 'ignored' }
  const { foreign, ...expected } = value
  assert.deepEqual(await readHostVersions(async () => JSON.stringify(value)), expected)
})
test('missing plugin, forbidden requests and disconnects are nonfatal', async () => {
  for (const error of ['PLUGIN_MISSING', 'PERMISSION_DENIED', 'DISCONNECTED']) {
    assert.deepEqual(await readHostVersions(async () => { throw Error(error) }), {})
  }
})
test('malformed, nonobject and unbounded responses are rejected', async () => {
  for (const raw of [null, {}, 'null', '[]', 'bad', 'x'.repeat(16385)]) {
    assert.deepEqual(await readHostVersions(async () => raw), {})
  }
})
test('invalid individual fields cannot overwrite valid versions', async () => {
  assert.deepEqual(await readHostVersions(async () => JSON.stringify({ 'xoa-proxy': 5, 'xo-lite-ce': 'bad\ntext', 'xcp-hl-release': '', iso:'ce56' })), {iso:'ce56'})
})
