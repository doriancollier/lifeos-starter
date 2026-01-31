#!/usr/bin/env python3
"""
Prompt Timestamp Hook (UserPromptSubmit)

Outputs the current date and time at the start of every user prompt.
"""

import json
import os
import sys
import time
from datetime import datetime

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("prompt-timestamp")


def main():
    """Main hook execution."""
    start = time.time()

    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        input_data = {}

    # Get current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    day_of_week = now.strftime("%A")
    timezone = now.astimezone().tzname()

    # Build context string
    context = f"Current time: {day_of_week}, {timestamp} {timezone}"

    # Output for UserPromptSubmit hook
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context
        }
    }

    print(json.dumps(output))

    log_hook_execution(logger, "UserPromptSubmit",
                      duration=time.time()-start, status="success")
    sys.exit(0)

if __name__ == "__main__":
    main()
