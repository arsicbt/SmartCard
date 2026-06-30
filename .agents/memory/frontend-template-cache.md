---
name: Frontend Jinja template caching
description: Why frontend HTML edits don't appear until the workflow restarts
---

# Frontend template cache requires workflow restart

Editing any file under `Frontend/templates/` (including `components/*.html`
partials) does NOT take effect on the served pages until the **"Start
application"** workflow is restarted. The frontend Flask app serves the cached
Jinja template; a hard browser refresh alone is not enough.

**Why:** the frontend Flask app does not have Jinja auto-reload / debug enabled,
so templates are compiled once and cached in memory per process.

**How to apply:** after any `Frontend/templates/**` edit, run
`restart_workflow("Start application")`, then verify with
`curl -s localhost:5000/<route>` (check the served HTML actually contains the
change) before screenshotting or concluding the fix works.
