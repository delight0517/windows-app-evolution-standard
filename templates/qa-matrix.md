# Focused hot-reload QA matrix

| Case | Fixture | Expected result | Evidence |
|---|---|---|---|
| Valid isolated reload | disposable profile, synthetic module | new generation/version; user data unchanged | API/state report |
| Init failure | candidate throws during init | previous source/module/version restored | hashes + rollback status |
| Stale candidate | canonical source changes after staging | apply rejected; restage required | source/base hashes |
| Alternate path | sibling worktree or path traversal | rejected before stage | validation error |
| Active work | synthetic request/write/auth/media flag | reload blocked with reason | blocker list |
| Watch debounce | file written in multiple chunks | one apply after stable content | observation/apply log |
| Stop while queued | callback queued, watcher stopped | callback inert; stays disabled | generation/status |
| Stop during apply | controlled delayed initializer | bounded finish or explicit timeout; never restarts | status before/after |
| State preservation | draft/settings/chat fixture | exact values retained | before/after state hashes/counts |
| Single instance | second launch attempt | existing process selected; no duplicate | PID inventory |
| Visual change | isolated non-activating capture | expected layout; no clipping | actual pixels + bounds |
| Restart-bound change | core/native fixture | declared restart/build gate; no false live claim | process version/build ID |

Record `PASS`, `FAIL`, `BLOCKED`, or `NOT RUN`; do not convert an unobserved visual check into a pass.

