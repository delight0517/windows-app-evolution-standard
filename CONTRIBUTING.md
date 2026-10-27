# Contributing

Keep the standard stack-neutral and concise. When adding a new procedure:

1. State the failure mode it prevents and the evidence that supports the rule.
2. Prefer a checklist, template, or small dependency-free validator over repeating long instructions in multiple files.
3. Keep security, user-state preservation, and restart/runtime boundaries explicit.
4. Add synthetic tests for validator behavior. Never use private app data, real credentials, or live provider calls as fixtures.
5. Update `SOP.md`, examples, and version together. Keep the personal Codex skill synchronized with the core workflow.

