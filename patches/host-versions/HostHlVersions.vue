<template>
  <VtsQuickInfoRow label="xcp-hl-release" :value="versions['xcp-hl-release'] ?? t('unknown')" />
  <VtsQuickInfoRow label="xo-lite-ce" :value="versions['xo-lite-ce'] ?? t('unknown')" />
  <VtsQuickInfoRow label="xoa-proxy" :value="versions['xoa-proxy'] ?? t('unknown')" />
  <VtsQuickInfoRow label="XCP-HL ISO" :value="versions.iso ?? host.software_version.build_number ?? t('unknown')" />
</template>

<script setup lang="ts">
import { readHostVersions, type HostVersions } from '@/libs/hl-host-versions'
import type { XenApiHost } from '@/libs/xen-api/xen-api.types'
import { useXenApiStore } from '@/stores/xen-api.store'
import VtsQuickInfoRow from '@core/components/quick-info-row/VtsQuickInfoRow.vue'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { host } = defineProps<{ host: XenApiHost }>()
const { t } = useI18n()
const xenApiStore = useXenApiStore()
const versions = ref<HostVersions>({})

watch(
  () => host.$ref,
  async (hostRef, _previous, onCleanup) => {
    let active = true
    onCleanup(() => { active = false })
    versions.value = {}
    const result = await readHostVersions(() =>
      xenApiStore.getXapi().call<string>('host.call_plugin', [hostRef, 'xcp-hl-versions', 'versions', {}])
    )
    if (active) versions.value = result
  },
  { immediate: true }
)
</script>
