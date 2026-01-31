#!/usr/bin/env python3
"""
Calendar Protection Hook (PreToolUse)

Intercepts calendar modification operations and requires confirmation for:
- Deleting any calendar event
- Modifying recurring events
- Updating events with attendees (will send notifications)

This hook prevents accidental calendar modifications.
"""

import json
import os
import sys
import time

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("calendar-protection")


def main():
    """Main hook execution."""
    start = time.time()

    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        log_hook_execution(logger, "PreToolUse", status="error",
                          details={"error": "Invalid JSON input"})
        input_data = {}

    # Get the tool name and input
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only intercept calendar modification tools
    calendar_modify_tools = [
        "mcp__google-calendar__delete-event",
        "mcp__google-calendar__update-event",
    ]

    if tool_name not in calendar_modify_tools:
        # Allow non-calendar tools to proceed
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "decision": "approve"
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # For delete operations, always require confirmation
    if tool_name == "mcp__google-calendar__delete-event":
        event_id = tool_input.get("eventId", "unknown")
        calendar_id = tool_input.get("calendarId", "unknown")

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "decision": "block",
                "reason": f"🛡️ Calendar Protection: Deleting event '{event_id}' from calendar '{calendar_id}' requires explicit user confirmation. Please confirm with the user before proceeding."
            }
        }
        print(json.dumps(output))

        log_hook_execution(logger, "PreToolUse", tool=tool_name,
                          duration=time.time()-start, status="warning",
                          details={"blocked": True, "action": "delete",
                                   "event_id": event_id})
        sys.exit(0)

    # For update operations, warn about attendees and recurring events
    if tool_name == "mcp__google-calendar__update-event":
        warnings = []

        # Check if updating attendees (will send notifications)
        if "attendees" in tool_input:
            warnings.append("This will send notification emails to attendees")

        # Check if modifying recurring event scope
        if "modificationScope" in tool_input:
            scope = tool_input.get("modificationScope", "")
            if scope in ["thisAndFollowing", "all"]:
                warnings.append(f"This will modify multiple instances of a recurring event (scope: {scope})")

        # Check for significant time changes
        if "start" in tool_input or "end" in tool_input:
            warnings.append("This changes the event time")

        if warnings:
            warning_text = "; ".join(warnings)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "decision": "block",
                    "reason": f"🛡️ Calendar Protection: {warning_text}. Please confirm with the user before proceeding."
                }
            }
            print(json.dumps(output))

            log_hook_execution(logger, "PreToolUse", tool=tool_name,
                              duration=time.time()-start, status="warning",
                              details={"blocked": True, "action": "update",
                                       "warnings": warnings})
            sys.exit(0)

    # Allow the operation if no concerns
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "decision": "approve"
        }
    }
    print(json.dumps(output))

    log_hook_execution(logger, "PreToolUse", tool=tool_name,
                      duration=time.time()-start, status="success")
    sys.exit(0)


if __name__ == "__main__":
    main()
