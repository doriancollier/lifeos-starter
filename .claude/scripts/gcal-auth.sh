#!/bin/bash
# Re-authenticate Google Calendar MCP server
# Run this when calendar auth expires (every 7 days in test mode)

GOOGLE_OAUTH_CREDENTIALS="{{vault_path}}/gcp-oauth.keys.json" \
  npx @cocal/google-calendar-mcp auth
