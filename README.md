# endurain-mcp

MCP server for [Endurain](https://github.com/endurain-project/endurain) – a self-hosted fitness tracking platform.

Exposes the full Endurain REST API as MCP tools over **stdio**, installable with `uvx`.

## Installation & usage

### With uvx (recommended)

```bash
uvx endurain-mcp --from git+https://github.com/jnmcfly/endurain-mcp.git
```

### With Claude Desktop / any MCP client

Add to your MCP client config:

```json
{
  "mcpServers": {
    "endurain": {
      "command": "uvx",
      "args": ["endurain-mcp"],
      "env": {
        "ENDURAIN_BASE_URL": "http://localhost:8080",
        "ENDURAIN_USERNAME": "admin",
        "ENDURAIN_PASSWORD": "admin"
      }
    }
  }
}
```

## Configuration

| Environment variable  | Required | Description                              |
|-----------------------|----------|------------------------------------------|
| `ENDURAIN_BASE_URL`   | yes      | Base URL of your Endurain instance       |
| `ENDURAIN_USERNAME`   | yes      | Login username                           |
| `ENDURAIN_PASSWORD`   | yes      | Login password                           |

## Available tools

### Activities
| Tool | Description |
|------|-------------|
| `list_activities` | Paginated activity list with optional filters |
| `get_activity` | Fetch a single activity by ID |
| `get_activities_count` | Total count with optional filters |
| `get_activities_this_week` | Distance totals for the current week |
| `get_activities_this_month` | Distance totals for the current month |
| `get_activities_week` | Activities for a relative week (0 = this week) |
| `get_activity_types` | Distinct activity types used by the user |
| `edit_activity` | Update name, description, visibility, gear |
| `delete_activity` | Delete an activity permanently |
| `get_activity_streams` | GPS/sensor stream data |
| `get_activity_laps` | Lap breakdown |
| `refresh_activities` | Trigger Strava/Garmin sync for last 24 h |

### Health
| Tool | Description |
|------|-------------|
| `list_sleep` / `get_sleep` / `get_sleep_by_date` | Sleep records |
| `create_sleep` / `edit_sleep` / `delete_sleep` | Manage sleep data |
| `get_sleep_count` | Total sleep record count |
| `list_weight` / `get_weight` | Weight records |
| `create_weight` / `delete_weight` | Manage weight data |
| `get_weight_count` | Total weight record count |
| `list_steps` / `get_steps` | Daily step records |
| `create_steps` / `delete_steps` | Manage step data |
| `get_steps_count` | Total steps record count |
| `list_health_targets` / `create_health_target` / `delete_health_target` | Health goals |

### Gear
| Tool | Description |
|------|-------------|
| `list_gears` / `get_gear` | Gear inventory |
| `create_gear` / `edit_gear` / `delete_gear` | Manage gear |
| `list_gear_components` / `create_gear_component` / `delete_gear_component` | Component tracking |
| `get_activities_by_gear` | Activities linked to a gear item |

### Users & Social
| Tool | Description |
|------|-------------|
| `get_me` | Authenticated user profile |
| `list_users` / `get_user` | User directory (admin) |
| `create_user` / `edit_user` / `delete_user` | User management (admin) |
| `get_users_count` | Total registered users |
| `list_sessions` / `delete_session` | Session management |
| `list_followers` / `list_following` | Follower/following lists |
| `follow_user` / `unfollow_user` | Social actions |

### Profile & Settings
| Tool | Description |
|------|-------------|
| `list_goals` / `create_goal` / `delete_goal` | Fitness goals |
| `list_default_gear` / `set_default_gear` / `delete_default_gear` | Per-sport default gear |
| `list_notifications` / `mark_notifications_read` | Notification inbox |
| `get_server_settings` / `edit_server_settings` | Server config (admin) |

## Authentication

The server authenticates using Endurain's **mobile client** OAuth2 password flow:

1. `POST /api/v1/auth/login` → obtains `access_token` + `refresh_token`
2. Access token is sent as `Authorization: Bearer <token>` on every request
3. Token is refreshed automatically before expiry; if refresh fails, a full re-login is performed

## Development

```bash
# Create and activate venv
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v

# Lint
ruff check src tests
```
