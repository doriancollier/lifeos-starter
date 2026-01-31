#!/usr/bin/env python3
"""
Email Reader - AppleScript wrapper for reading macOS Mail.app

Usage:
    # Read operations
    python email_reader.py accounts              # List all accounts
    python email_reader.py unread                # Get unread counts
    python email_reader.py recent [account] [n]  # Get n recent emails
    python email_reader.py unread-list [account] [n]  # Get n unread emails
    python email_reader.py body [account] [index]     # Get email body
    python email_reader.py search [account] [query]   # Search by sender
    python email_reader.py search-subject [account] [query]  # Search by subject
    python email_reader.py search-body [account] [query] [n] # Search body content
    python email_reader.py search-archive [query] [field] [n] # Fast SQLite search (requires FDA)

    # Write operations
    python email_reader.py mark-read [account] [index]    # Mark as read
    python email_reader.py mark-unread [account] [index]  # Mark as unread
    python email_reader.py delete [account] [index]       # Move to trash
    python email_reader.py move-spam [account] [index]    # Move to spam

    # Note: Archive is NOT supported via AppleScript (Gmail limitation).
    # See Gmail API Migration project for future solution.

All functions return JSON for easy parsing.
"""

import subprocess
import json
import sys
import sqlite3
import os
from datetime import datetime
from typing import Optional

# Mail database path (requires Full Disk Access)
MAIL_DB_PATH = os.path.expanduser("~/Library/Mail/V10/MailData/Envelope Index")


def run_applescript(script: str, timeout: int = 30) -> str:
    """Run AppleScript and return output."""
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=timeout
    )
    if result.returncode != 0:
        raise Exception(f"AppleScript error: {result.stderr}")
    return result.stdout.strip()


def get_accounts() -> list[dict]:
    """Get all Mail.app accounts with their email addresses and mailboxes."""
    script = '''
    tell application "Mail"
        set accountData to {}
        repeat with acct in accounts
            set acctName to name of acct
            set acctEmails to email addresses of acct
            set mailboxNames to name of every mailbox of acct
            -- Join mailbox names with semicolon delimiter
            set AppleScript's text item delimiters to ";"
            set mailboxStr to mailboxNames as string
            set AppleScript's text item delimiters to ""
            set end of accountData to "ACCOUNT:" & acctName & "|EMAIL:" & (item 1 of acctEmails) & "|MAILBOXES:" & mailboxStr
        end repeat
        return accountData
    end tell
    '''
    output = run_applescript(script)

    accounts = []
    for line in output.split(", ACCOUNT:"):
        line = line.replace("ACCOUNT:", "")
        if "|EMAIL:" in line and "|MAILBOXES:" in line:
            parts = line.split("|EMAIL:")
            name = parts[0]
            rest = parts[1].split("|MAILBOXES:")
            email = rest[0]
            mailboxes = rest[1].split(";") if rest[1] else []
            accounts.append({
                "name": name,
                "email": email,
                "mailboxes": mailboxes
            })

    return accounts


def get_unread_counts() -> dict:
    """Get unread email count for each account's INBOX."""
    script = '''
    tell application "Mail"
        set unreadData to {}
        repeat with acct in accounts
            set acctName to name of acct
            try
                set inboxUnread to unread count of mailbox "INBOX" of acct
                set end of unreadData to acctName & ":" & inboxUnread
            end try
        end repeat
        return unreadData
    end tell
    '''
    output = run_applescript(script)

    counts = {}
    for item in output.split(", "):
        if ":" in item:
            parts = item.split(":")
            counts[parts[0]] = int(parts[1])

    return counts


def get_recent_emails(account: Optional[str] = None, count: int = 10, unread_only: bool = False) -> list[dict]:
    """
    Get recent emails from specified account or all accounts.

    Args:
        account: Account name (e.g., "Google" or "{{work_email}}"). None for all.
        count: Number of emails to retrieve (default 10)
        unread_only: If True, only get unread emails
    """
    if account:
        filter_clause = "whose read status is false" if unread_only else ""
        script = f'''
        tell application "Mail"
            set emailData to {{}}
            set msgList to (every message of mailbox "INBOX" of account "{account}" {filter_clause})
            set msgCount to count of msgList
            if msgCount > {count} then set msgCount to {count}

            repeat with i from 1 to msgCount
                set msg to item i of msgList
                set msgSubject to subject of msg
                set msgSender to sender of msg
                set msgDate to date received of msg
                set msgRead to read status of msg
                set msgId to id of msg
                set end of emailData to "ID:" & msgId & "|FROM:" & msgSender & "|SUBJECT:" & msgSubject & "|DATE:" & (msgDate as string) & "|READ:" & msgRead & "|ACCOUNT:{account}"
            end repeat
            return emailData
        end tell
        '''
    else:
        # Get from all accounts
        filter_clause = "whose read status is false" if unread_only else ""
        script = f'''
        tell application "Mail"
            set emailData to {{}}
            repeat with acct in accounts
                set acctName to name of acct
                try
                    set msgList to (every message of mailbox "INBOX" of acct {filter_clause})
                    set msgCount to count of msgList
                    if msgCount > {count} then set msgCount to {count}

                    repeat with i from 1 to msgCount
                        set msg to item i of msgList
                        set msgSubject to subject of msg
                        set msgSender to sender of msg
                        set msgDate to date received of msg
                        set msgRead to read status of msg
                        set msgId to id of msg
                        set end of emailData to "ID:" & msgId & "|FROM:" & msgSender & "|SUBJECT:" & msgSubject & "|DATE:" & (msgDate as string) & "|READ:" & msgRead & "|ACCOUNT:" & acctName
                    end repeat
                end try
            end repeat
            return emailData
        end tell
        '''

    output = run_applescript(script)

    emails = []
    for line in output.split(", ID:"):
        line = line.replace("ID:", "")
        if "|FROM:" in line:
            email = {}
            parts = line.split("|")
            for part in parts:
                if part.startswith("FROM:"):
                    email["from"] = part[5:]
                elif part.startswith("SUBJECT:"):
                    email["subject"] = part[8:]
                elif part.startswith("DATE:"):
                    email["date"] = part[5:]
                elif part.startswith("READ:"):
                    email["read"] = part[5:] == "true"
                elif part.startswith("ACCOUNT:"):
                    email["account"] = part[8:]
                elif not ":" in part:
                    email["id"] = part
                else:
                    # Handle ID at start
                    email["id"] = part.split(":")[0] if ":" not in part else part
            if "id" not in email:
                email["id"] = line.split("|")[0]
            emails.append(email)

    return emails


def get_email_body(account: str, message_index: int = 1) -> dict:
    """
    Get the body content of a specific email.

    Args:
        account: Account name
        message_index: 1-based index of the message in INBOX
    """
    script = f'''
    tell application "Mail"
        set msg to message {message_index} of mailbox "INBOX" of account "{account}"
        set msgSubject to subject of msg
        set msgSender to sender of msg
        set msgContent to content of msg
        return "SUBJECT:" & msgSubject & "|FROM:" & msgSender & "|BODY:" & msgContent
    end tell
    '''
    output = run_applescript(script)

    result = {"account": account}
    if "|FROM:" in output and "|BODY:" in output:
        parts = output.split("|FROM:")
        result["subject"] = parts[0].replace("SUBJECT:", "")
        rest = parts[1].split("|BODY:")
        result["from"] = rest[0]
        result["body"] = rest[1] if len(rest) > 1 else ""

    return result


def search_archive(query: str, search_field: str = "all", count: int = 20) -> list[dict]:
    """
    Fast READ-ONLY search across ALL emails using Mail's SQLite database.
    Requires Full Disk Access permission.

    SAFETY MEASURES:
    - Database opened in READ-ONLY mode (mode=ro) - writes are impossible
    - All user input is parameterized (?) - prevents SQL injection
    - search_field is validated against whitelist - no dynamic SQL from user input
    - count is validated as integer - prevents injection

    Args:
        query: Search string (parameterized, safe from injection)
        search_field: "sender", "subject", or "all" (default) - validated whitelist
        count: Max results to return (validated integer)

    Returns:
        List of matching emails with subject, sender, date
    """
    # === SAFETY VALIDATIONS ===
    # Whitelist validation for search_field - prevents SQL injection
    ALLOWED_FIELDS = {"sender", "subject", "all"}
    if search_field not in ALLOWED_FIELDS:
        search_field = "all"  # Default to safe value

    # Validate count is reasonable
    count = min(max(1, int(count)), 100)  # Clamp between 1 and 100

    if not os.path.exists(MAIL_DB_PATH):
        return [{"error": "Mail database not found. Ensure Full Disk Access is granted."}]

    try:
        # CRITICAL: mode=ro ensures READ-ONLY access - database cannot be modified
        conn = sqlite3.connect(f"file:{MAIL_DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()

        # Pre-defined WHERE clauses (not built from user input)
        # User's query value is ALWAYS passed via parameterized ? placeholder
        WHERE_CLAUSES = {
            "sender": "a.address LIKE ?",
            "subject": "s.subject LIKE ?",
            "all": "(a.address LIKE ? OR s.subject LIKE ?)"
        }

        where_clause = WHERE_CLAUSES[search_field]

        # Build params - user input is NEVER interpolated into SQL
        if search_field == "all":
            params = [f"%{query}%", f"%{query}%", count]
        else:
            params = [f"%{query}%", count]

        # Static SQL template - only ? placeholders, no string formatting of user input
        sql = f"""
        SELECT m.ROWID, m.date_received, s.subject, a.address, mb.url
        FROM messages m
        JOIN subjects s ON m.subject = s.ROWID
        JOIN addresses a ON m.sender = a.ROWID
        LEFT JOIN mailboxes mb ON m.mailbox = mb.ROWID
        WHERE {where_clause}
        ORDER BY m.date_received DESC
        LIMIT ?
        """

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        emails = []
        for row in rows:
            msg_id, date_received, subject, sender, mailbox_url = row
            # Convert timestamp to readable date (already Unix format in Mail DB)
            if date_received:
                date_str = datetime.fromtimestamp(date_received).strftime("%Y-%m-%d %H:%M")
            else:
                date_str = "Unknown"

            # Extract account from mailbox URL
            account = "Unknown"
            if mailbox_url:
                if "{{user_email}}" in mailbox_url or "Google" in mailbox_url:
                    account = "Google"
                elif "{{company_1_domain}}" in mailbox_url:
                    account = "{{work_email}}"

            emails.append({
                "id": msg_id,
                "date": date_str,
                "subject": subject,
                "from": sender,
                "account": account,
                "source": "sqlite_archive"
            })

        return emails

    except Exception as e:
        return [{"error": f"Database query failed: {str(e)}"}]


def search_emails_in_mailbox(account: str, mailbox: str, query: str, search_field: str, count: int) -> tuple[list[dict], str]:
    """
    Search emails in a specific mailbox. Returns (results, mailbox_name).
    """
    field_map = {"sender": "sender", "subject": "subject"}
    field = field_map.get(search_field, "sender")

    script = f'''
    tell application "Mail"
        set emailData to {{}}
        try
            set msgList to (every message of mailbox "{mailbox}" of account "{account}" whose {field} contains "{query}")
            set msgCount to count of msgList
            if msgCount > {count} then set msgCount to {count}

            repeat with i from 1 to msgCount
                set msg to item i of msgList
                set msgSubject to subject of msg
                set msgSender to sender of msg
                set msgDate to date received of msg
                set end of emailData to "FROM:" & msgSender & "|SUBJECT:" & msgSubject & "|DATE:" & (msgDate as string)
            end repeat
        end try
        return emailData
    end tell
    '''
    output = run_applescript(script)

    emails = []
    for line in output.split(", FROM:"):
        line = line.replace("FROM:", "")
        if "|SUBJECT:" in line:
            email = {"account": account, "mailbox": mailbox}
            parts = line.split("|SUBJECT:")
            email["from"] = parts[0]
            rest = parts[1].split("|DATE:")
            email["subject"] = rest[0]
            email["date"] = rest[1] if len(rest) > 1 else ""
            emails.append(email)

    return emails, mailbox


def search_emails(account: str, query: str, search_field: str = "sender", count: int = 10, expand_search: bool = True) -> list[dict]:
    """
    Search emails by sender or subject. Automatically expands to smaller mailboxes if INBOX empty.

    Args:
        account: Account name
        query: Search string
        search_field: "sender" or "subject"
        count: Max results to return
        expand_search: If True, search Sent Mail and other folders if INBOX has no results

    Note: Does NOT search [Gmail]/All Mail due to timeout issues (400k+ messages).
    For archived Gmail, use Mail.app UI search or Gmail web interface.
    """
    # Search order: INBOX first, then Sent Mail (reasonable size folders only)
    # Intentionally excludes [Gmail]/All Mail which has 400k+ messages and times out
    mailboxes_to_search = ["INBOX"]
    if expand_search:
        mailboxes_to_search.extend(["Sent Mail", "Starred", "Important"])

    for mailbox in mailboxes_to_search:
        emails, found_in = search_emails_in_mailbox(account, mailbox, query, search_field, count)
        if emails:
            # Add metadata about where results were found
            for email in emails:
                email["found_in_mailbox"] = found_in
            return emails

    return []


def search_body(account: str, query: str, count: int = 5, search_limit: int = 20) -> list[dict]:
    """
    Search emails by body content. Note: This is slower than other searches.

    Args:
        account: Account name
        query: Search string to find in email body
        count: Max results to return (default 5)
        search_limit: Max emails to search through (default 20, max 50)
    """
    search_limit = min(search_limit, 50)  # Cap at 50 to prevent timeouts
    script = f'''
    tell application "Mail"
        set emailData to {{}}
        set msgs to messages 1 thru {search_limit} of mailbox "INBOX" of account "{account}"
        set foundCount to 0

        repeat with msg in msgs
            if foundCount >= {count} then exit repeat
            try
                set msgContent to content of msg
                if msgContent contains "{query}" then
                    set msgSubject to subject of msg
                    set msgSender to sender of msg
                    set msgDate to date received of msg
                    set msgId to id of msg
                    set end of emailData to "ID:" & msgId & "|FROM:" & msgSender & "|SUBJECT:" & msgSubject & "|DATE:" & (msgDate as string)
                    set foundCount to foundCount + 1
                end if
            end try
        end repeat
        return emailData
    end tell
    '''
    output = run_applescript(script, timeout=120)  # 2 minute timeout for body search

    emails = []
    for line in output.split(", ID:"):
        line = line.replace("ID:", "")
        if "|FROM:" in line:
            email = {"account": account}
            parts = line.split("|FROM:")
            email["id"] = parts[0]
            rest = parts[1].split("|SUBJECT:")
            email["from"] = rest[0]
            rest2 = rest[1].split("|DATE:") if len(rest) > 1 else ["", ""]
            email["subject"] = rest2[0]
            email["date"] = rest2[1] if len(rest2) > 1 else ""
            emails.append(email)

    return emails


def mark_read(account: str, message_index: int) -> dict:
    """Mark an email as read."""
    script = f'''
    tell application "Mail"
        set msg to message {message_index} of mailbox "INBOX" of account "{account}"
        set subj to subject of msg
        set read status of msg to true
        return "Marked as read: " & subj
    end tell
    '''
    output = run_applescript(script)
    return {"success": True, "message": output, "account": account, "index": message_index}


def mark_unread(account: str, message_index: int) -> dict:
    """Mark an email as unread."""
    script = f'''
    tell application "Mail"
        set msg to message {message_index} of mailbox "INBOX" of account "{account}"
        set subj to subject of msg
        set read status of msg to false
        return "Marked as unread: " & subj
    end tell
    '''
    output = run_applescript(script)
    return {"success": True, "message": output, "account": account, "index": message_index}


def delete_email(account: str, message_index: int) -> dict:
    """Move an email to trash."""
    script = f'''
    tell application "Mail"
        set msg to message {message_index} of mailbox "INBOX" of account "{account}"
        set subj to subject of msg
        set trashBox to mailbox "Trash" of account "{account}"
        move msg to trashBox
        return "Moved to trash: " & subj
    end tell
    '''
    output = run_applescript(script)
    return {"success": True, "message": output, "account": account, "index": message_index}


def move_to_spam(account: str, message_index: int) -> dict:
    """Move an email to spam folder."""
    script = f'''
    tell application "Mail"
        set msg to message {message_index} of mailbox "INBOX" of account "{account}"
        set subj to subject of msg
        set spamBox to mailbox "Spam" of account "{account}"
        move msg to spamBox
        return "Moved to spam: " & subj
    end tell
    '''
    output = run_applescript(script)
    return {"success": True, "message": output, "account": account, "index": message_index}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "accounts":
            result = get_accounts()
        elif command == "unread":
            result = get_unread_counts()
        elif command == "recent":
            account = sys.argv[2] if len(sys.argv) > 2 else None
            count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            result = get_recent_emails(account, count)
        elif command == "unread-list":
            account = sys.argv[2] if len(sys.argv) > 2 else None
            count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            result = get_recent_emails(account, count, unread_only=True)
        elif command == "body":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            index = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            result = get_email_body(account, index)
        elif command == "search":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            query = sys.argv[3] if len(sys.argv) > 3 else ""
            result = search_emails(account, query)
        elif command == "search-subject":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            query = sys.argv[3] if len(sys.argv) > 3 else ""
            result = search_emails(account, query, search_field="subject")
        elif command == "search-body":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            query = sys.argv[3] if len(sys.argv) > 3 else ""
            count = int(sys.argv[4]) if len(sys.argv) > 4 else 10
            result = search_body(account, query, count)
        elif command == "search-archive":
            # Fast SQLite search across ALL emails (requires FDA)
            query = sys.argv[2] if len(sys.argv) > 2 else ""
            field = sys.argv[3] if len(sys.argv) > 3 else "all"  # sender, subject, or all
            count = int(sys.argv[4]) if len(sys.argv) > 4 else 20
            result = search_archive(query, field, count)
        elif command == "mark-read":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            index = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            result = mark_read(account, index)
        elif command == "mark-unread":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            index = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            result = mark_unread(account, index)
        elif command == "delete":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            index = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            result = delete_email(account, index)
        elif command == "move-spam":
            account = sys.argv[2] if len(sys.argv) > 2 else "Google"
            index = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            result = move_to_spam(account, index)
        else:
            print(f"Unknown command: {command}")
            print(__doc__)
            sys.exit(1)

        print(json.dumps(result, indent=2, default=str))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
