export type GuestIdentity = { application: string; image?: string }

/** Display-only guest data. It is never an authorization or release-QA input. */
export function parseGuestIdentity(metrics: unknown, now = Date.now()): GuestIdentity | null {
  if (metrics === null || typeof metrics !== 'object') return null
  const record = metrics as Record<string, unknown>
  if (record.live !== true || record.other === null || typeof record.other !== 'object') return null
  const raw = (record.other as Record<string, unknown>)['xoa-hl-identity']
  if (typeof raw !== 'string' || raw.length > 1024) return null
  try {
    const identity: unknown = JSON.parse(raw)
    if (identity === null || typeof identity !== 'object' || Array.isArray(identity)) return null
    const value = identity as Record<string, unknown>
    if (value.schema !== 1 || value.product !== 'xoa-hl') return null
    if (typeof value.reported_at !== 'string' || value.reported_at.length !== 20 || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value.reported_at)) return null
    const age = now - Date.parse(value.reported_at)
    if (!Number.isFinite(age) || age > 15 * 60_000 || age < -5 * 60_000) return null
    if (typeof value.application !== 'string' || /[\u0000-\u001f\u007f]/.test(value.application) || !/^[A-Za-z0-9_.:+-]{1,256}$/.test(value.application)) return null
    const image = typeof value.image === 'string' && !/[\u0000-\u001f\u007f]/.test(value.image) && (
      /^xoa-image-[0-9]{8}(?:-[0-9]{15})?-[0-9a-f]{7,40}$/.test(value.image) ||
      /^built [0-9]{4}-[0-9]{2}-[0-9]{2}, commit [0-9a-f]{7,40}, release v[A-Za-z0-9_.+-]{1,160}$/.test(value.image)
    ) ? value.image : undefined
    return { application: value.application, image }
  } catch {
    return null
  }
}
