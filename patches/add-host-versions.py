#!/usr/bin/env python3
"""Install the host version card on the pinned XO Lite source; fail on drift."""
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parent / 'host-versions'
TARGET = Path('@xen-orchestra/lite/src')

def apply(root):
    root = Path(root) / TARGET
    page = root / 'components/host/system/HostSystemGeneralInformation.vue'
    text = page.read_text()
    anchor = '    <VtsQuickInfoRow :label="t(\'name\')" :value="host.name_label" />'
    imports = '<script setup lang="ts">'
    if text.count(anchor) != 1 or text.count(imports) != 1 or 'HostHlVersions' in text:
        raise ValueError('unexpected pinned HostSystemGeneralInformation.vue')
    text = text.replace(anchor, '    <HostHlVersions :host="host" />\n' + anchor)
    text = text.replace(imports, imports + "\nimport HostHlVersions from '@/components/host/system/HostHlVersions.vue'")
    # Validate source/assets before writing into the build checkout.
    component = (SOURCE/'HostHlVersions.vue').read_text()
    helper = (SOURCE/'hl-host-versions.ts').read_text()
    page.write_text(text)
    (page.parent/'HostHlVersions.vue').write_text(component)
    (root/'libs/hl-host-versions.ts').write_text(helper)

if __name__ == '__main__': apply(sys.argv[1])
