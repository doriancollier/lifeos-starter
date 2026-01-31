# Email Reader Skill

Read and manage emails from macOS Mail.app using AppleScript integration.

## Activation

Activate this skill when:
- User asks about emails, inbox, or unread messages
- User wants to check email from specific accounts
- Meeting prep or person context needs recent email history
- Daily planning involves email triage
- User asks to process, triage, or clean up inbox

## Available Accounts

| Account Name | Email Address | Primary Use |
|-------------|---------------|-------------|
| Google | {{user_email}} | Personal |
| {{work_email}} | {{work_email}} | {{company_1_name}} |

## Usage

### Via Python Script

The `email_reader.py` script provides callable functions:

```bash
# ===== READ OPERATIONS =====

# List all accounts and mailboxes
python3 .claude/skills/email-reader/email_reader.py accounts

# Get unread counts per account
python3 .claude/skills/email-reader/email_reader.py unread

# Get recent emails (all accounts)
python3 .claude/skills/email-reader/email_reader.py recent

# Get recent emails from specific account
python3 .claude/skills/email-reader/email_reader.py recent "Google" 5

# Get unread emails only
python3 .claude/skills/email-reader/email_reader.py unread-list "{{work_email}}" 10

# Get email body content (by index)
python3 .claude/skills/email-reader/email_reader.py body "Google" 1

# Search by sender
python3 .claude/skills/email-reader/email_reader.py search "Google" "alex"

# Search by subject
python3 .claude/skills/email-reader/email_reader.py search-subject "Google" "invoice"

# Search by body content (slower, 2 min timeout)
python3 .claude/skills/email-reader/email_reader.py search-body "Google" "domain" 5

# ===== WRITE OPERATIONS =====

# Mark email as read (by index)
python3 .claude/skills/email-reader/email_reader.py mark-read "Google" 1

# Mark email as unread
python3 .claude/skills/email-reader/email_reader.py mark-unread "Google" 1

# Move to trash
python3 .claude/skills/email-reader/email_reader.py delete "Google" 1

# Move to spam
python3 .claude/skills/email-reader/email_reader.py move-spam "Google" 1

# NOTE: Archive is NOT supported - see limitations below
```

### Via Direct AppleScript

For quick queries, use `osascript` directly:

```bash
# Get account names
osascript -e 'tell application "Mail" to get name of every account'

# Get unread count
osascript -e 'tell application "Mail" to get unread count of mailbox "INBOX" of account "Google"'

# Get recent email subjects
osascript -e 'tell application "Mail"
    set msgs to messages 1 thru 5 of mailbox "INBOX" of account "Google"
    set subjects to {}
    repeat with msg in msgs
        set end of subjects to subject of msg
    end repeat
    return subjects
end tell'
```

## Python API Reference

### Read Functions

#### `get_accounts() -> list[dict]`
Returns all configured Mail.app accounts with email addresses and mailbox names.

#### `get_unread_counts() -> dict`
Returns unread count for each account's INBOX.

#### `get_recent_emails(account=None, count=10, unread_only=False) -> list[dict]`
Get recent emails with optional filters.
- `account`: Account name (None for all accounts)
- `count`: Number of emails to retrieve
- `unread_only`: Filter to unread emails only

#### `get_email_body(account, message_index=1) -> dict`
Get the full body content of a specific email by index.

#### `search_emails(account, query, search_field="sender", count=10, expand_search=True) -> list[dict]`
Search emails by sender or subject. **Automatically expands search** to All Mail and Archive if INBOX has no results. Results include `found_in_mailbox` field showing where the email was found.

#### `search_body(account, query, count=5, search_limit=20) -> list[dict]`
Search emails by body content. Slower due to reading each email body.

#### `search_archive(query, search_field="all", count=20) -> list[dict]`
**Fast SQLite search** across ALL emails (requires Full Disk Access). Searches 400k+ emails instantly.
- `query`: Search string
- `search_field`: "sender", "subject", or "all" (default)
- `count`: Max results (default 20)

### Write Functions

#### `mark_read(account, message_index) -> dict`
Mark an email as read by index.

#### `mark_unread(account, message_index) -> dict`
Mark an email as unread by index.

#### `delete_email(account, message_index) -> dict`
Move an email to trash by index.

#### `move_to_spam(account, message_index) -> dict`
Move an email to spam folder by index.

## Email Data Structure

Each email returns:
```json
{
  "id": "12345",
  "from": "sender@example.com",
  "subject": "Email subject line",
  "date": "Thursday, December 4, 2025 at 10:00:00 AM",
  "read": false,
  "account": "Google",
  "found_in_mailbox": "All Mail"  // Search results only - shows where found
}
```

**Search behavior**: When searching, if no results in INBOX, automatically searches Sent Mail, Starred, and Important folders. The `found_in_mailbox` field indicates where results were found. Note: Does NOT search [Gmail]/All Mail due to performance issues (see limitations).

## Common Use Cases

### Morning Email Triage
```bash
# Check what needs attention
python3 .claude/skills/email-reader/email_reader.py unread
python3 .claude/skills/email-reader/email_reader.py unread-list "Google" 10
```

### Meeting Prep - Recent Communication
```bash
# Find emails from meeting attendee
python3 .claude/skills/email-reader/email_reader.py search "Google" "attendee@company.com"
```

### Context Switching
```bash
# Check {{company_1_name}} inbox when switching context
python3 .claude/skills/email-reader/email_reader.py recent "{{work_email}}" 5
```

### Find Important Emails
```bash
# Search for urgent items
python3 .claude/skills/email-reader/email_reader.py search-subject "Google" "urgent"
python3 .claude/skills/email-reader/email_reader.py search-subject "Google" "action required"
```

### Clean Up Inbox
```bash
# Find and delete spam (confirm with user first!)
python3 .claude/skills/email-reader/email_reader.py search "Google" "marketing@"
# Then: python3 .claude/skills/email-reader/email_reader.py move-spam "Google" [index]
```

## Heavy Email Operations

For comprehensive inbox processing (triage, summarization, bulk operations), use the **email-processor agent** via Task tool. This isolates large data operations from the main conversation context.

Example:
```
Task: email-processor
Prompt: "Triage my Google inbox. Categorize unread emails into: action required, FYI, spam/newsletter, automated. Recommend which to delete."
```

## Limitations

- **Mail.app required**: Must be configured with accounts in Apple Mail
- **Local only**: Reads from local mail cache, may not have latest emails if not synced
- **Performance**: Body searches are slower (2 min timeout) due to reading each email
- **Index-based**: Write operations use message index which can shift if inbox changes

### Gmail Archive NOT Supported

**Archive is not available via AppleScript.** Gmail uses labels instead of folders, and AppleScript cannot remove the INBOX label - it can only move messages between folders. Moving to `[Gmail]/All Mail` doesn't archive; the email stays in both INBOX and All Mail.

**Workaround**: Use `mark-read` to dismiss emails, then manually archive via Mail.app UI when convenient.

**Future**: See `1-Projects/Backlog/Gmail API Migration.md` for planned Gmail API integration that will enable proper archiving.

### Gmail Archive Search

Gmail archived emails are stored in `[Gmail]/All Mail` which typically contains 100k-400k+ messages. AppleScript's `whose` search clause times out on mailboxes this large.

**Solution: Use `search-archive` command**

With Full Disk Access granted, the `search-archive` command queries Mail's SQLite database directly - searching 400k+ emails in under a second:

```bash
# Search all archived emails (sender + subject)
python3 .claude/skills/email-reader/email_reader.py search-archive "british airways"

# Search by sender only
python3 .claude/skills/email-reader/email_reader.py search-archive "ba.com" sender

# Search by subject only
python3 .claude/skills/email-reader/email_reader.py search-archive "e-ticket" subject 20
```

**Requirements:**
- Full Disk Access must be granted to Terminal/IDE
- Mail.app must be configured with accounts

**Note:** Standard AppleScript searches (`search`, `search-subject`) still work for INBOX and smaller folders but cannot search large archives efficiently.

## Safety Notes

### Database Safety (Critical)

The `search-archive` command accesses Mail's SQLite database with these protections:

1. **READ-ONLY mode**: Database opened with `?mode=ro` - writes are impossible at SQLite level
2. **Parameterized queries**: All user input uses `?` placeholders - prevents SQL injection
3. **Whitelist validation**: `search_field` only accepts predefined values (sender/subject/all)
4. **Function encapsulation**: All database access goes through `search_archive()` function only

**NEVER**:
- Write raw SQL queries outside of defined functions
- Pass user input directly into SQL strings
- Attempt to modify the Mail database

### Email Operations Safety

- **Confirm before deleting**: Always show email details before delete/spam operations
- **Index volatility**: Message indices change as inbox changes - verify before batch operations
- **Work email caution**: Be extra careful with {{company_1_name}} account modifications

## Integration Points

- **daily-note skill**: Can reference email counts in daily planning
- **meeting-prep skill**: Can pull recent emails from meeting attendees
- **person-context skill**: Can show recent email history with a person
- **email-processor agent**: For heavy triage and batch operations
