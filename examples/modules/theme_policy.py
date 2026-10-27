"""Synthetic example of a pure policy module with explicit state hooks."""
API_VERSION = 1
VERSION = "1.0.0"


def resolve(preference, system_mode="light"):
    if preference in {"light", "dark"}:
        return preference
    return "dark" if preference == "system" and system_mode == "dark" else "light"


def initialize(host, api):
    host.theme_policy = resolve
    return {"previous": getattr(host, "theme_policy", None), "actions": []}


def snapshot_state(host, handle):
    return {"preference": getattr(host, "theme_preference", "light")}


def restore_state(host, api, handle, snapshot):
    host.theme_preference = snapshot["preference"]


def shutdown(host, handle):
    host.theme_policy = (handle or {}).get("previous")
