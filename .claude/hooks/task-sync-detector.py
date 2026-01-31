#!/usr/bin/env python3
"""
Task Sync Detector - PostToolUse Hook

Detects when task-related changes are made to daily notes or project files
and queues them for synchronization.

This hook:
1. Triggers on Write/Edit to files in 1-Projects/ or 4-Daily/
2. Detects task patterns in the content
3. Writes sync requirements to .claude/sync-queue.json
4. Returns a reminder for Claude to process the sync

Hook Event: PostToolUse
Tools: Write, Edit
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add hooks directory to path for hook_logger import
sys.path.insert(0, os.path.dirname(__file__))
from hook_logger import setup_logger, log_hook_execution

# Initialize logger
logger = setup_logger("task-sync-detector")

# Vault configuration - uses environment variable or auto-detects from script location
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_ROOT") or str(Path(__file__).resolve().parent.parent.parent)
SYNC_QUEUE_FILE = os.path.join(VAULT_ROOT, ".claude", "sync-queue.json")
PROJECTS_DIR = os.path.join(VAULT_ROOT, "1-Projects", "Current")
DAILY_DIR = os.path.join(VAULT_ROOT, "4-Daily")

# Task patterns
TASK_PATTERN = re.compile(r'^- \[([ x])\] (.+)$', re.MULTILINE)
PROJECT_SECTION_PATTERN = re.compile(r'^####\s+\[\[([^\]]+)\]\]', re.MULTILINE)
PRIORITY_PATTERN = re.compile(r'[🔴🟡🟢🔵]')

def extract_tasks(content: str) -> list[dict]:
    """Extract tasks from file content."""
    tasks = []
    for match in TASK_PATTERN.finditer(content):
        completed = match.group(1) == 'x'
        text = match.group(2).strip()
        # Strip priority emoji for matching
        clean_text = PRIORITY_PATTERN.sub('', text).strip()
        # Remove numbering like "1. " or "2. "
        clean_text = re.sub(r'^\d+\.\s*', '', clean_text)
        tasks.append({
            'raw': match.group(0),
            'text': text,
            'clean_text': clean_text,
            'completed': completed,
            'position': match.start()
        })
    return tasks

def find_project_section(content: str, position: int) -> Optional[str]:
    """Find which project section a task belongs to based on position."""
    sections = list(PROJECT_SECTION_PATTERN.finditer(content))
    if not sections:
        return None

    # Find the section that contains this position
    for i, section in enumerate(sections):
        section_start = section.start()
        # If there's a next section, task must be before it
        if i + 1 < len(sections):
            next_start = sections[i + 1].start()
            if section_start <= position < next_start:
                return section.group(1)
        else:
            # Last section - task belongs here if after section start
            if position >= section_start:
                return section.group(1)

    return None

def is_daily_note(file_path: str) -> bool:
    """Check if file is a daily note."""
    return DAILY_DIR in file_path and file_path.endswith('.md')

def is_project_file(file_path: str) -> bool:
    """Check if file is a project file."""
    return PROJECTS_DIR in file_path and file_path.endswith('.md')

def load_sync_queue() -> list:
    """Load existing sync queue."""
    if os.path.exists(SYNC_QUEUE_FILE):
        try:
            with open(SYNC_QUEUE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_sync_queue(queue: list):
    """Save sync queue."""
    os.makedirs(os.path.dirname(SYNC_QUEUE_FILE), exist_ok=True)
    with open(SYNC_QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def queue_sync(source_file: str, source_type: str, task_info: dict, project_name: str = None):
    """Add a sync task to the queue."""
    queue = load_sync_queue()

    entry = {
        'timestamp': datetime.now().isoformat(),
        'source_file': source_file,
        'source_type': source_type,  # 'daily' or 'project'
        'project': project_name,
        'task_text': task_info['clean_text'],
        'completed': task_info['completed'],
        'processed': False
    }

    # Avoid duplicate entries
    for existing in queue:
        if (existing['source_file'] == entry['source_file'] and
            existing['task_text'] == entry['task_text'] and
            existing['completed'] == entry['completed']):
            return  # Already queued

    queue.append(entry)
    save_sync_queue(queue)

def main():
    start = time.time()

    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        # Not valid JSON, pass through
        log_hook_execution(logger, "PostToolUse", status="error",
                          details={"error": "Invalid JSON input"})
        print(json.dumps({"status": "success"}))
        return

    tool_name = hook_input.get('tool_name', '')
    tool_input = hook_input.get('tool_input', {})
    tool_result = hook_input.get('tool_result', '')

    # Only process Write and Edit tools
    if tool_name not in ['Write', 'Edit']:
        print(json.dumps({"status": "success"}))
        return

    file_path = tool_input.get('file_path', '')

    # Check if it's a relevant file
    if not (is_daily_note(file_path) or is_project_file(file_path)):
        print(json.dumps({"status": "success"}))
        return

    # Read the file content
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except IOError as e:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="error",
                          details={"error": str(e), "file": file_path})
        print(json.dumps({"status": "success"}))
        return

    # Extract tasks
    tasks = extract_tasks(content)
    if not tasks:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="success",
                          details={"file": os.path.basename(file_path), "tasks": 0})
        print(json.dumps({"status": "success"}))
        return

    # Determine source type and queue syncs
    syncs_queued = 0

    if is_daily_note(file_path):
        # For daily notes, find project context for each task
        for task in tasks:
            project = find_project_section(content, task['position'])
            if project:
                queue_sync(file_path, 'daily', task, project)
                syncs_queued += 1

    elif is_project_file(file_path):
        # For project files, extract project name from path
        project_name = Path(file_path).stem
        # Check if in subdirectory (like AssetOps/AssetOps.md)
        parent = Path(file_path).parent.name
        if parent != 'Current':
            project_name = parent

        for task in tasks:
            queue_sync(file_path, 'project', task, project_name)
            syncs_queued += 1

    # If syncs were queued, remind Claude
    if syncs_queued > 0:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="success",
                          details={"file": os.path.basename(file_path),
                                   "syncs_queued": syncs_queued})
        print(json.dumps({
            "status": "success",
            "message": f"Task changes detected in {Path(file_path).name}. {syncs_queued} task(s) queued for sync. Consider using the task-sync skill to reconcile with counterpart files."
        }))
    else:
        log_hook_execution(logger, "PostToolUse", tool=tool_name,
                          duration=time.time()-start, status="success",
                          details={"file": os.path.basename(file_path), "syncs_queued": 0})
        print(json.dumps({"status": "success"}))

if __name__ == "__main__":
    main()
