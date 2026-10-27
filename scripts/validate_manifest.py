#!/usr/bin/env python3
"""Validate a modular-app manifest without installing dependencies."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath

ID_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
ALLOWED_SUFFIXES = {".py", ".js", ".ts", ".dll", ".so", ".dylib"}


def validate(root: Path, manifest_path: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    path = manifest_path if manifest_path.is_absolute() else root / manifest_path
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"manifest_read_error:{type(exc).__name__}"]
    if not isinstance(manifest, dict):
        return ["manifest_must_be_object"]
    if not isinstance(manifest.get("api_version"), int) or manifest["api_version"] < 1:
        errors.append("manifest_api_version_must_be_positive_integer")
    modules = manifest.get("modules")
    if not isinstance(modules, list) or not modules:
        return errors + ["modules_must_be_nonempty_list"]

    by_id: dict[str, dict] = {}
    order: dict[str, int] = {}
    for index, item in enumerate(modules):
        label = f"modules[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label}_must_be_object")
            continue
        module_id = item.get("id")
        if not isinstance(module_id, str) or not ID_RE.fullmatch(module_id):
            errors.append(f"{label}_invalid_id")
            continue
        if module_id in by_id:
            errors.append(f"duplicate_module_id:{module_id}")
        else:
            by_id[module_id] = item
            order[module_id] = index
        if not isinstance(item.get("version"), str) or not item["version"].strip():
            errors.append(f"{module_id}_version_required")
        if not isinstance(item.get("api_version"), int) or item["api_version"] < 1:
            errors.append(f"{module_id}_api_version_invalid")
        dependencies = item.get("dependencies")
        if (not isinstance(dependencies, list)
                or any(not isinstance(dep, str) or not ID_RE.fullmatch(dep) for dep in dependencies)
                or len(set(dependencies)) != len(dependencies)):
            errors.append(f"{module_id}_dependencies_invalid")
        for field in ("reloadable", "restart_required", "auto_watch"):
            if not isinstance(item.get(field), bool):
                errors.append(f"{module_id}_{field}_must_be_boolean")
        if item.get("reloadable") is True and item.get("restart_required") is True:
            errors.append(f"{module_id}_reloadable_restart_required_conflict")

        module_path = item.get("path")
        if not isinstance(module_path, str) or not module_path:
            errors.append(f"{module_id}_path_required")
        else:
            posix = PurePosixPath(module_path)
            if (posix.is_absolute() or ".." in posix.parts or "\\" in module_path
                    or len(posix.parts) < 2 or posix.parts[0] not in {"modules", "extensions"}
                    or Path(posix.name).suffix.lower() not in ALLOWED_SUFFIXES):
                errors.append(f"{module_id}_path_not_canonical_relative_source")
            else:
                candidate = root.joinpath(*posix.parts)
                try:
                    resolved = candidate.resolve(strict=False)
                    if root not in resolved.parents:
                        errors.append(f"{module_id}_path_escapes_root")
                    elif not candidate.is_file():
                        errors.append(f"{module_id}_source_file_missing")
                except OSError:
                    errors.append(f"{module_id}_path_unresolvable")

        lifecycle = item.get("lifecycle")
        if not isinstance(lifecycle, dict) or not all(
                isinstance(lifecycle.get(key), str) and lifecycle[key].strip()
                for key in ("initialize", "dispose")):
            errors.append(f"{module_id}_lifecycle_initialize_dispose_required")
        if item.get("auto_watch") is True:
            if item.get("reloadable") is not True or item.get("restart_required") is True:
                errors.append(f"{module_id}_auto_watch_requires_reloadable_module")
            if (not isinstance(lifecycle, dict)
                    or not all(isinstance(lifecycle.get(key), str) and lifecycle[key].strip()
                               for key in ("snapshot_state", "restore_state"))):
                errors.append(f"{module_id}_auto_watch_requires_snapshot_restore")

    for module_id, item in by_id.items():
        deps = item.get("dependencies", [])
        if not isinstance(deps, list):
            continue
        for dep in deps:
            if dep not in by_id:
                errors.append(f"{module_id}_unknown_dependency:{dep}")
            elif (item.get("startup", True) and by_id[dep].get("startup", True)
                  and order[dep] >= order[module_id]):
                errors.append(f"{module_id}_startup_dependency_order:{dep}")

    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(module_id: str) -> None:
        if module_id in visiting:
            errors.append(f"dependency_cycle:{module_id}")
            return
        if module_id in visited:
            return
        visiting.add(module_id)
        for dep in by_id[module_id].get("dependencies", []):
            if dep in by_id:
                visit(dep)
        visiting.remove(module_id)
        visited.add(module_id)
    for module_id in by_id:
        visit(module_id)

    allowlist = manifest.get("watch_allowlist", [])
    if not isinstance(allowlist, list) or any(not isinstance(item, str) for item in allowlist):
        errors.append("watch_allowlist_must_be_string_list")
    else:
        if len(set(allowlist)) != len(allowlist):
            errors.append("watch_allowlist_contains_duplicates")
        for module_id in allowlist:
            item = by_id.get(module_id)
            if item is None:
                errors.append(f"watch_allowlist_unknown_module:{module_id}")
            elif item.get("auto_watch") is not True:
                errors.append(f"watch_allowlist_module_not_opted_in:{module_id}")
        for module_id, item in by_id.items():
            if item.get("auto_watch") is True and module_id not in allowlist:
                errors.append(f"{module_id}_auto_watch_missing_from_allowlist")
    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="canonical app source root")
    parser.add_argument("--manifest", default="module-manifest.json", type=Path)
    args = parser.parse_args(argv)
    errors = validate(args.root, args.manifest)
    print(json.dumps({"ok": not errors, "error_count": len(errors), "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
