# Login translation source review — xcp-hl#283

Baseline: `xo-lite-v0.21.0` / `13f987ff3d34504a90b89178489e15fa2293d1b3`.

`AppLogin.vue` incorrectly uses the action key `login` for the read-only root username field. Change only that label to `username`; retain `login` for the submit button and title. Password labels/placeholders already use `password`. `LoginError.vue` uses `password-invalid` and `error-occurred`; `PoolOverrideWarning.vue` adds `you-are-currently-on` and `click-to-return-default-pool`.

All 21 registered locale catalogs were inspected for the nine login-page keys (including the pool-override warning). Existing French username text is correct; fixing the component makes it visible. Add missing translations explicitly, fix Russian remember-me semantics (previously “keep me informed”), and use European Portuguese username terminology in `pt`.

| Locale | Missing login keys before correction | Changes |
| --- | --- | --- |
| cs | None | Existing strings retained |
| da | keep-me-logged, login-only-on-master, password-invalid | keep-me-logged, login-only-on-master, password-invalid |
| de | None | Existing strings retained |
| en | None | Existing strings retained |
| es | None | Existing strings retained |
| fa | username | username |
| fi | login, login-only-on-master, password-invalid, you-are-currently-on, click-to-return-default-pool | login, login-only-on-master, password-invalid, you-are-currently-on, click-to-return-default-pool |
| fr | None | Existing strings retained |
| it | keep-me-logged, login-only-on-master | keep-me-logged, login-only-on-master |
| ja | username, login, keep-me-logged, login-only-on-master, password-invalid, error-occurred, you-are-currently-on, click-to-return-default-pool | username, login, keep-me-logged, login-only-on-master, password-invalid, error-occurred, you-are-currently-on, click-to-return-default-pool |
| ko | username, password, login, keep-me-logged, login-only-on-master, password-invalid, error-occurred, you-are-currently-on, click-to-return-default-pool | username, password, login, keep-me-logged, login-only-on-master, password-invalid, error-occurred, you-are-currently-on, click-to-return-default-pool |
| nb-NO | None | Existing strings retained |
| nl | None | Existing strings retained |
| pl | login, keep-me-logged, login-only-on-master, you-are-currently-on, click-to-return-default-pool | login, keep-me-logged, login-only-on-master, you-are-currently-on, click-to-return-default-pool |
| pt-BR | password, password-invalid, you-are-currently-on | password, password-invalid, you-are-currently-on |
| pt | None | username |
| ru | username, you-are-currently-on | username, keep-me-logged, you-are-currently-on |
| sk | None | Existing strings retained |
| sv | None | Existing strings retained |
| uk | username, login, keep-me-logged, login-only-on-master, you-are-currently-on | username, login, keep-me-logged, login-only-on-master, you-are-currently-on |
| zh-Hans | None | Existing strings retained |

This is a source/terminology review, not native-speaker approval or deployed-browser evidence. Native-language review, Japanese glyphs, RTL layout, accessible labels, focus, password errors and clipping remain to be checked on a released CE build. No authentication, editable username or credential behavior changes. The shared `login` action is not redefined.

No upstream PR submitted by this change. The field-key error is inherited from the pinned upstream source.
