"""Synthetic example only; replace with the host app's design-token contract."""
API_VERSION = 1
VERSION = "1.0.0"


def initialize(host, api):
    host.design_tokens = {"surface": "#ffffff", "text": "#222222"}
    return {"actions": []}


def shutdown(host, handle):
    host.design_tokens = None
