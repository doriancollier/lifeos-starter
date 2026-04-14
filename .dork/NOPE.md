# Safety Boundaries

## Never Do

- Never modify files in `.user/` (identity.yaml, coaching.yaml, etc.) without explicit approval
- Never delete daily notes, meeting notes, or person files
- Never expose personal data (health metrics, relationships, financial info) outside the vault
- Never skip the pre-commit guard that prevents personal data commits
- Never delete calendar events without confirmation (calendar-protection hook)
- Never override the directory guard for protected paths
- Never commit the `workspace/` directory or any personal vault content

## Always Do

- Always validate frontmatter when writing to vault files
- Always validate task format (A/B/C system) when creating tasks
- Always load session context at start (session-context-loader)
- Always respect the `.user/` configuration as the source of truth for personalization
- Always maintain planning horizon connections (daily → weekly → monthly → quarterly → annual)
