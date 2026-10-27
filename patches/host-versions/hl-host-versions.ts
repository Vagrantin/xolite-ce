export const VERSION_KEYS = ['xcp-hl-release', 'xo-lite-ce', 'xoa-proxy', 'iso'] as const
export type HostVersions = Partial<Record<(typeof VERSION_KEYS)[number], string>>

/** Treat plugin responses as data; absent/old/unauthorized plugins show Unknown. */
export async function readHostVersions(load: () => Promise<unknown>): Promise<HostVersions> {
  try {
    const raw = await load()
    if (typeof raw !== 'string' || raw.length > 16384) return {}
    const parsed: unknown = JSON.parse(raw)
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) return {}
    const record = parsed as Record<string, unknown>
    const versions: HostVersions = {}
    for (const key of VERSION_KEYS) {
      const value = record[key]
      if (typeof value === 'string' && value.length > 0 && value.length <= 256 && !/[\u0000-\u001f\u007f]/.test(value)) {
        versions[key] = value
      }
    }
    return versions
  } catch {
    return {}
  }
}
