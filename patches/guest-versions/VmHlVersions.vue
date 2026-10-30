<template>
  <template v-if="identity !== null">
    <VtsQuickInfoRow label="XOA-HL" :value="identity.application" />
    <VtsQuickInfoRow label="XOA-HL VM" :value="identity.image ?? t('unknown')" />
  </template>
</template>

<script setup lang="ts">
import { parseGuestIdentity } from '@/libs/hl-guest-identity'
import type { XenApiVmGuestMetrics } from '@/libs/xen-api/xen-api.types'
import VtsQuickInfoRow from '@core/components/quick-info-row/VtsQuickInfoRow.vue'
import { useNow } from '@vueuse/core'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { metrics } = defineProps<{ metrics?: XenApiVmGuestMetrics }>()
const { t } = useI18n()
const now = useNow({ interval: 60_000 })
const identity = computed(() => parseGuestIdentity(metrics, now.value.getTime()))
</script>
