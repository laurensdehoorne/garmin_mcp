[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/taxuspt-garmin-mcp-badge.png)](https://mseep.ai/app/taxuspt-garmin-mcp)

# Garmin MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects to Garmin Connect and exposes your fitness and health data to Claude and other MCP-compatible clients.

Garmin's API is accessed via the [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) library.

## Tool Coverage

**130 tools** covering 100% of the [python-garminconnect](https://github.com/cyberjunky/python-garminconnect) library (v0.3.3):

| Module | Tools |
|--------|-------|
| Activity Management | 21 |
| Health & Wellness | 33 |
| Training & Performance | 12 |
| Workouts | 10 |
| Challenges & Badges | 11 |
| Nutrition | 8 |
| Devices | 6 |
| Gear Management | 5 |
| Weight Tracking | 6 |
| Data Management | 4 |
| User Profile | 4 |
| Women's Health | 3 |
| Golf | 3 |

## Setup

### Step 1: Authenticate

Run the pre-authentication tool once before using the server:

```bash
uvx --python 3.12 --from git+https://github.com/laurensdehoorne/garmin_mcp garmin-mcp-auth
```

This saves OAuth tokens to `~/.garminconnect`. You will not need credentials in your MCP config after this.

**Options:**
```bash
# Verify existing tokens
garmin-mcp-auth --verify

# Force re-authentication
garmin-mcp-auth --force-reauth

# Use custom token location
garmin-mcp-auth --token-path ~/.garmin_tokens

# Garmin Connect China
garmin-mcp-auth --is-cn
```

### Step 2: Configure Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        "git+https://github.com/laurensdehoorne/garmin_mcp",
        "garmin-mcp"
      ]
    }
  }
}
```

If Claude Desktop can't find `uvx`, use its full path (find it with `which uvx`).

### Step 3: Restart Claude Desktop

Your Garmin data is now available in Claude.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GARMIN_EMAIL` | Garmin Connect email |
| `GARMIN_EMAIL_FILE` | Path to file containing email |
| `GARMIN_PASSWORD` | Garmin Connect password |
| `GARMIN_PASSWORD_FILE` | Path to file containing password |
| `GARMIN_IS_CN` | Set `true` for Garmin Connect China |
| `GARMINTOKENS` | Token storage path (default: `~/.garminconnect`) |

You cannot set both `GARMIN_EMAIL` and `GARMIN_EMAIL_FILE` simultaneously.

## Garmin Connect China

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uvx",
      "args": ["--python", "3.12", "--from", "git+https://github.com/laurensdehoorne/garmin_mcp", "garmin-mcp"],
      "env": { "GARMIN_IS_CN": "true" }
    }
  }
}
```

## Run from Local Repository

```json
{
  "mcpServers": {
    "garmin-local": {
      "command": "uv",
      "args": ["--directory", "/path/to/garmin_mcp", "run", "garmin-mcp"]
    }
  }
}
```

## Docker

```bash
# Create .env with credentials
echo "GARMIN_EMAIL=your@email.com" > .env
echo "GARMIN_PASSWORD=yourpassword" >> .env

# Start
docker compose up -d
```

For MFA with Docker, run interactively first:
```bash
docker compose run --rm garmin-mcp
```
Tokens are saved to the `garmin-tokens` volume and reused on subsequent runs.

## Local Development

```bash
uv sync
npx @modelcontextprotocol/inspector uv run garmin-mcp
```

## Testing

```bash
# Integration tests (mocked Garmin API)
uv run pytest tests/integration/ -v

# End-to-end tests (requires real credentials)
uv run pytest tests/e2e/ -m e2e -v
```

## Troubleshooting

**MFA error: "no interactive terminal available"**  
Run `garmin-mcp-auth` in a terminal, then restart Claude Desktop.

**Token expired / invalid**  
Run `garmin-mcp-auth --force-reauth`.

**Logs**  
- macOS: `~/Library/Logs/Claude/mcp-server-garmin.log`  
- Windows: `%APPDATA%\Claude\logs\mcp-server-garmin.log`

> **Upgrading from v0.2.x?** Tokens are not compatible with v0.3.x. Delete `~/.garminconnect` and run `garmin-mcp-auth`.
