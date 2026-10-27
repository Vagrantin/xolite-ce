import assert from 'node:assert/strict'
import test from 'node:test'
import { parseGuestIdentity } from '../patches/guest-versions/hl-guest-identity.ts'
const now=Date.parse('2026-10-28T01:02:03Z')
const identity={schema:1,product:'xoa-hl',application:'5.113.2_e281c536-47.gca44911.xcpng8.3.el9',image:'xoa-image-20261028-010203000000001-abcdef0',reported_at:'2026-10-28T01:02:03Z'}
const metrics=(value=identity, live=true)=>({live,other:{'xoa-hl-identity':JSON.stringify(value)}})

test('current installed and exact image versions are read from this VM metrics',()=>{
  assert.deepEqual(parseGuestIdentity(metrics(),now),{application:identity.application,image:identity.image})
})
test('legacy image stamps remain readable and absent image is Unknown',()=>{
  const legacy='built 2026-10-22, commit a280852, release v5.113.2_e281c536-ce40'
  assert.equal(parseGuestIdentity(metrics({...identity,image:legacy}),now).image,legacy)
  assert.equal(parseGuestIdentity(metrics({...identity,image:null}),now).image,undefined)
})
test('offline, expired and implausibly future reports are not displayed',()=>{
  assert.equal(parseGuestIdentity(metrics(identity,false),now),null)
  assert.equal(parseGuestIdentity(metrics(),now+16*60_000),null)
  assert.equal(parseGuestIdentity(metrics(),now-6*60_000),null)
})
test('missing metrics and malformed or unrelated reports are ignored',()=>{
  for(const record of [undefined,null,{},metrics(null),metrics({...identity,schema:2}),metrics({...identity,product:'other'}),{live:true,other:{'xoa-hl-identity':'bad'}},metrics({...identity,reported_at:'bad'})]){
    assert.equal(parseGuestIdentity(record,now),null)
  }
})
test('control characters, oversize payload and fabricated object versions are rejected',()=>{
  assert.equal(parseGuestIdentity(metrics({...identity,application:'bad\nvalue'}),now),null)
  assert.equal(parseGuestIdentity(metrics({...identity,application:{value:'bad'}}),now),null)
  assert.equal(parseGuestIdentity(metrics({...identity,image:'<img src=x onerror=alert(1)>'}),now).image,undefined)
  assert.equal(parseGuestIdentity(metrics({...identity,extra:'x'.repeat(1025)}),now),null)
})
