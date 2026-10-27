# Windows App Evolution Standard

A compact, reusable standard for safely evolving Windows desktop apps through modular features, source-level hot reload, isolated QA, and guarded restarts.

This package distills a real Python/Tkinter implementation. It is written for any Windows stack: adapt the UI dispatcher, lifecycle hooks, secure storage, and runtime boundary to the framework. The Python manifest checker is an optional reference utility, not a required runtime dependency.

## What is included

- `SOP.md` — the implementation and QA procedure.
- `templates/` — project card, module contract, and focused QA matrix.
- `schema/module-manifest.schema.json` — a JSON Schema for the example manifest format.
- `scripts/validate_manifest.py` — a standard-library validator for identity, paths, dependencies, watcher allowlists, and lifecycle declarations.
- `tests/` — synthetic validator checks.
- `LICENSE` — MIT License.

## Quick start

1. Copy `templates/project-card.md` into the target app's project notes and complete it before changing source or launching a candidate.
2. Map the current app into feature modules and record the exact runtime apply boundary.
3. Define the manifest and module lifecycle before adding automatic reload.
4. Run `python scripts/validate_manifest.py --root <app-root> --manifest <manifest-path>`.
5. Run isolated synthetic lifecycle, stale-candidate, stop-race, and state-preservation checks before any live promotion.

See [SOP.md](SOP.md) for the full workflow and acceptance gates.

## Scope

This repository contains reusable guidance and a generic validator only. It does not contain the Software Tutor application, its user data, account credentials, or private QA reports. Hot reload executes trusted code in the host application's security context; it is not a sandbox.

