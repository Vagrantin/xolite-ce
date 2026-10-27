# Japanese pool dashboard — xcp-hl#295

Scope: XO Lite `xo-lite-v0.21.0` at upstream commit
`13f987ff3d34504a90b89178489e15fa2293d1b3`.

The upstream Japanese web-core catalog lacks the reported dashboard and
unreachable-host dialog keys. The Vue components already call `t()`; their
English text is a locale fallback. No component or upstream pin change is needed.

`patches/ja-pool-dashboard.json` supplies 36 Japanese messages: the 34 missing
literal keys used by the pool dashboard cards, tabs and unreachable-host dialog,
plus the two shared status messages targeted by host and VM status links.
This includes the reported Hosts/VMs tabs, active/inactive counters, Load now,
and all four dialog messages. Other dashboard card headings, loading/error
messages and interpolation placeholders are covered in the same pass.

The RPM workflow applies `update-ja-pool-dashboard.py` after the existing login
locale correction and before the UI build. It changes only the Japanese catalog,
validates English key existence and interpolation placeholders, and rejects
missing or circular Japanese message links before writing.

`ci/test-ja-pool-dashboard.py` reads the actual pinned dashboard Vue consumers,
checks their literal translation keys and linked targets without English fallback,
retains login fixes and unrelated Japanese messages, verifies every other locale
is byte-for-byte unchanged, and exercises validation failures and repeat application.
GitHub Actions runs this check on PRs; builds remain in the existing RPM workflow.

Validation boundary: this is source/catalog coverage, including empty/loading
states. It does not certify all dynamically generated alarm descriptions, shared
table components or the rest of XO Lite's Japanese interface. A released RPM still
needs live browser validation: select Japanese, check the pool dashboard including
the alarms Load now state, open the unreachable-host dialog on a multi-host lab,
and check Japanese glyphs, wrapping and reload behavior. Record the RPM NEVRA and
Jenkins capture build with that evidence.
