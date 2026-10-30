#!/usr/bin/env python3
"""Install guest version rows into the pinned VM System card; fail on drift."""
from pathlib import Path
import sys

SOURCE=Path(__file__).resolve().parent/'guest-versions'
TARGET=Path('@xen-orchestra/lite/src')

def apply(root):
    root=Path(root)/TARGET
    page=root/'components/vm/system/VmGeneralInfo.vue'
    text=page.read_text()
    anchor='    <VtsQuickInfoRow :label="t(\'management-agent-version\')" :value="pvVersion" />'
    script='<script setup lang="ts">'
    if text.count(anchor)!=1 or text.count(script)!=1 or 'VmHlVersions' in text:
        raise ValueError('unexpected pinned VmGeneralInfo.vue')
    component=(SOURCE/'VmHlVersions.vue').read_text()
    helper=(SOURCE/'hl-guest-identity.ts').read_text()
    text=text.replace(anchor,anchor+'\n    <VmHlVersions :metrics="guestMetrics" />').replace(script,script+"\nimport VmHlVersions from '@/components/vm/system/VmHlVersions.vue'")
    page.write_text(text)
    (page.parent/'VmHlVersions.vue').write_text(component)
    (root/'libs/hl-guest-identity.ts').write_text(helper)

if __name__=='__main__':apply(sys.argv[1])
