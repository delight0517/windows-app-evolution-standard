# Windows App Evolution SOP

Version 0.1.0 · MIT · Reusable for Windows desktop applications and tools

## Purpose

Change only the feature that needs to change, apply reloadable source quickly, and keep user work, credentials, and the running app recoverable. Treat every result as one of four separate states: source edited, isolated candidate verified, installed/runtime updated, and real user/account behavior verified.

## 0. Establish identity and scope

Before editing, building, launching, restarting, or capturing, record a project card using `templates/project-card.md`:

- App/project ID, type, canonical source root, version, and branch/worktree or single-source status.
- User's objective, current project focus, exact process/PID/runtime owner, and allowed QA target.
- Included and excluded apps/data, dependencies consumed, modules changed, and the one owner for each shared file/runtime.
- Preservation plan for drafts, chats, attachments, settings, auth sessions, pending writes/jobs, and rollback.

Resolve conflicting project/source evidence read-only. Do not pick a similarly named folder, active process, or dependency as the target by guesswork. For another user's live app, never foreground, activate, restart, or read content without the exact authorization and safe-state gate.

## 1. Capture the baseline without disturbing the user

Inspect source instructions, TODO/handoff, module manifest, process executable/path/PID, app version, and recent integration claims. Use a read-only runtime API when available. Record only necessary state: window state, draft present/absent, pending files/jobs, requests/writes/callbacks, feature versions/hashes, and blocker names. Never log prompt/reply text, tokens, OAuth codes, or secret values.

Do not infer app behavior from source alone. Separate existing implementation, installed files, loaded module generation/hash, actual account connection, and pixels/user-visible result. Use non-activating capture; if minimized-window capture is unsupported, report visual verification as blocked instead of restoring it.

## 2. Define modules before implementation

Map the app into bounded features with stable versioned contracts: shell/navigation; product workflows; UI/design tokens/fonts; domain logic; AI/provider adapters; persistence; media/background work; and platform/native integration. Keep UI, business rules, provider, and storage concerns independently reviewable. Put shared contracts under one integration owner.

For each module, record owned paths, dependencies, API version, init/dispose, state snapshot/restore, event/callback ownership, reloadability, and restart/build boundary in `templates/module-contract.md`. A module name or manifest flag alone does not prove safe reload. Start with stateless logic or isolated data/presentation contracts; defer live-widget and native changes until their teardown and restoration are testable.

## 3. Preserve one source of truth and prevent stale updates

- Keep one canonical checkout/install path. If Git is available, use a named branch/worktree per independent feature and integrate sequentially; do not leave multiple uncommitted variants competing for the same module.
- Assign one writer per file and one owner for integration/runtime. Record those claims in the project card. If there is no Git repository, say so; do not invent branch/commit provenance.
- Stage only allowlisted module files from the canonical root. Reject path traversal, symlink/reparse escapes, sibling worktrees, build/install copies, and arbitrary workspace candidates.
- Bind every staged candidate to module ID, canonical root/relative path, source SHA-256, loaded base SHA-256, API version, and runtime generation. Recheck all fields immediately before apply. A changed source/base/generation means restage, never guess.
- Serialize stage/apply/rollback per module across the process boundary, or enforce a verified single-instance host. Preserve the current live bytes plus two verified rollback copies (or the project's explicitly tested equivalent). Verify backup hashes before pruning.

Use `schema/module-manifest.schema.json` and the validator as a starting point. Example:

```json
{
  "api_version": 1,
  "watch_allowlist": ["theme_policy"],
  "modules": [{
    "id": "theme_policy",
    "path": "modules/theme_policy.py",
    "version": "1.0.0",
    "api_version": 1,
    "dependencies": [],
    "reloadable": true,
    "restart_required": false,
    "auto_watch": true,
    "lifecycle": {
      "initialize": "initialize",
      "dispose": "shutdown",
      "snapshot_state": "snapshot_state",
      "restore_state": "restore_state"
    }
  }]
}
```

## 4. Implement lifecycle and reload boundaries

The host owns a single module manager and an explicit main-thread/UI dispatcher. A filesystem watcher or HTTP worker must never mutate UI objects directly. Every reload sequence should:

1. Check pending-work blockers: drafts, uploads, AI/provider requests, auth/token persistence, settings/history writes, media jobs, dialogs, callbacks, and active feature operations.
2. Validate candidate syntax, API contract, dependency order, source/base hashes, and runtime capability.
3. Snapshot module-owned state and registered actions/subscriptions.
4. Dispose old resources and callbacks exactly once; initialize the candidate; verify module version/hash and returned contract.
5. On failure, restore original source, old module, state, callbacks, and persisted version; report rollback failure separately.

Reload only the changed supported module. Core shell, manifest/registry, imported dependencies, native code, WebView/runtime binaries, registrations, and renderer settings may require app restart, reconnect, recompile, cook, or package. State the exact boundary before attempting an update. Do not call a source edit a live update until the target PID reports the new version/hash.

## 5. Add automatic watching only after manual reload is safe

Watcher defaults to off. Start/stop/status must be explicit, scoped, persisted atomically, visible, and testable. Persist disabled before stopping. Use a cancellation generation/epoch so queued callbacks cannot apply or re-enable the watcher after stop. If apply is already underway, stop waits for or reports its bounded completion; it must never claim stopped while more work can begin.

Watch only loaded modules explicitly opted into a reviewed allowlist. Ignore manifests, arbitrary files, staging/rollback folders, and native/core files. Debounce edits, require stable repeated content/hash, validate before apply, and dispatch through the host's UI thread. Keep blocked candidates visible and retry only while the watcher remains enabled. On syntax/init/rollback error, stop retrying that candidate and expose the error. Confirm loaded version and source hash after apply.

Never start an automation just to fill a UI. A stopped watcher must stay stopped across an in-flight update and after app restart. If persisted enabled intent is restored at startup, show that state and provide a working stop control.

## 6. Keep credentials and account state separate

Use provider-specific adapters and secure OS storage. Persist preferences, not plaintext credentials. Never trigger login/consent on startup or as a reload side effect. Serialize account changes against requests and keep chats/drafts/attachments. Verify safe persisted account/scopes and a fresh API call before diagnosing disconnection. Never print tokens or OAuth callback values.

## 7. Verify in isolated layers

Use `templates/qa-matrix.md` and synthetic local profiles. Do not make real provider requests, spend credits, access user chats, or start microphones/media in routine QA.

Minimum focused gates:

- Manifest/path/API/dependency validation; duplicate IDs, cycles, traversal/symlink escapes rejected.
- Module init/dispose/reload; state, settings, drafts, and callbacks preserved; failed init restores the previous source/version.
- Stale source/base/generation rejected; rollback hashes verified; unrelated modules remain loaded.
- Active request/write/auth/media/dialog blockers reject reload and show exact reasons.
- Watch debounce, stable file, candidate validation, pending blocker retry, stop while queued/in-flight, stop persistence across restart, and no accidental restart/re-enable.
- Single-instance behavior, no login-on-start, no native error dialog in hidden QA, bounded timeout/cleanup.
- Targeted end-to-end feature action in a disposable profile; visual/UI claims require actual non-activating pixels or clearly remain unverified.

Run the smallest relevant checks first, then integration smoke where module boundaries meet. Do not package the whole app for a source-only module edit. Preserve test reports outside user data; remove only the exact disposable profile created by the test.

## 8. Promote and report accurately

Promote only after blockers are empty and preservation is verified. Use one canonical installed path and the app's single-instance mechanism. Keep current plus two verified rollback versions. If core restart is required, preserve data and verify the exact target process before/after; never launch an extra competing copy.

Report: files/modules changed; source and branch/version; QA target and checks/results; current vs candidate vs installed/live module version; account/provider operation status; visual verification limit; rollback and restart/build boundary; unresolved work and next safe action. Never promise zero future errors or model retraining from written SOPs.

## Lessons carried forward

- The first watcher draft did not dispatch because it advanced the baseline hash before the stable-observation count completed. Test state transitions over multiple polling intervals, not only the final snapshot.
- Tk-backed modules must reload on the Tk/UI thread even when change detection runs in a worker thread.
- A staged candidate's own hash is insufficient; it must also match the current canonical source and the base generation that was loaded when staged.
- A minimized window may not support non-activating pixel capture. API state is useful evidence, not visual evidence.
- A successful source edit, hidden synthetic QA, installed file, live module version, and real user-account operation are distinct proof levels.

