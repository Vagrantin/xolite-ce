// Execute the actual common cleanup extracted from the patched pinned source.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const source = readFileSync(process.argv[2], 'utf8')
const cleanup = source.match(/    await Promise\.all\(\n      \['admin-account',[\s\S]*?\n    \)/g)
assert.equal(cleanup?.length, 1, 'unique common cleanup block')
const run = new Function('xapi', 'vmRef', `return (async () => { ${cleanup[0]} })()`)
for (const image of ['xoa-hl', 'vates', 'ronivay', 'custom']) {
  const data = new Map([
    ['vm-data/admin-account', 'synthetic-admin'],
    ['vm-data/system-account-xoa-password', 'synthetic-ssh'],
    ['vm-data/xoa-updater-credentials', 'synthetic-updater'],
    ['vm-data/unrelated', 'keep'],
  ])
  await run({ call: async (method, [vm, key]) => {
    assert.equal(method, 'VM.remove_from_xenstore_data')
    assert.equal(vm, image)
    data.delete(key)
  } }, { value: image })
  assert.deepEqual([...data], [['vm-data/unrelated', 'keep']])
}
await assert.rejects(run({ call: async () => { throw Error('XAPI unavailable') } }, { value: 'vm' }))
console.log('Deployment credential cleanup: all image sources, unrelated data, XAPI failure passed')
