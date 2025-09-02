This directory-based initial data layout is used by the load_initial_data management command.
Place JSON arrays in the following files (all fields should omit explicit "pk"):
- django_admin_users.json
- members.json (mapped to test users)
- resource_types.json
- building_types.json (image can be a static path like "static/img/campamento_principal.png" or "img/campamento_principal.png")
- rarities.json
- abilities.json
- heroes.json (image can be a static path under core/static/img)
- enemies.json
- building_costs.json

If this directory exists, it takes precedence over the legacy initial_data.json at project root.
