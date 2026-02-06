#!/usr/bin/env node
/**
 * Migration Script: Add processed: false to existing meeting files
 *
 * Adds the `processed` and `processed_date` fields to meeting.md files
 * that don't already have them. This enables the /meeting:process workflow.
 *
 * Usage:
 *   node migrate-add-processed.js              # Dry run (preview changes)
 *   node migrate-add-processed.js --apply      # Apply changes
 */

const fs = require('fs');
const path = require('path');

const VAULT_ROOT = path.resolve(__dirname, '../../..');
const MEETINGS_DIR = path.join(VAULT_ROOT, '5-Meetings');

const dryRun = !process.argv.includes('--apply');

console.log('🔄 Meeting Processing Migration');
console.log(`   Mode: ${dryRun ? 'DRY RUN (use --apply to make changes)' : 'APPLYING CHANGES'}`);
console.log('');

function findMeetingFiles(dir) {
  const results = [];

  if (!fs.existsSync(dir)) {
    return results;
  }

  const items = fs.readdirSync(dir, { withFileTypes: true });

  for (const item of items) {
    const fullPath = path.join(dir, item.name);

    if (item.isDirectory()) {
      results.push(...findMeetingFiles(fullPath));
    } else if (item.name === 'meeting.md') {
      results.push(fullPath);
    }
  }

  return results;
}

function parseYamlFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return { frontmatter: null, body: content };

  const frontmatterText = match[1];
  const body = content.slice(match[0].length);

  // Simple YAML parsing (key: value)
  const frontmatter = {};
  const lines = frontmatterText.split('\n');

  for (const line of lines) {
    const colonIndex = line.indexOf(':');
    if (colonIndex > 0) {
      const key = line.slice(0, colonIndex).trim();
      let value = line.slice(colonIndex + 1).trim();

      // Parse common YAML values
      if (value === 'true') value = true;
      else if (value === 'false') value = false;
      else if (value === 'null') value = null;
      else if (value.startsWith('"') && value.endsWith('"')) {
        value = value.slice(1, -1);
      } else if (value.startsWith('[') && value.endsWith(']')) {
        // Keep arrays as strings for simplicity
      }

      frontmatter[key] = value;
    }
  }

  return { frontmatter, body, originalFrontmatter: frontmatterText };
}

function addProcessedFields(content) {
  const { frontmatter, body, originalFrontmatter } = parseYamlFrontmatter(content);

  if (!frontmatter) {
    // No frontmatter, can't migrate
    return { updated: false, reason: 'no frontmatter' };
  }

  // Check if already has processed field
  if ('processed' in frontmatter) {
    return { updated: false, reason: 'already has processed field' };
  }

  // Add processed fields before the closing ---
  const newFrontmatter = originalFrontmatter + '\nprocessed: false\nprocessed_date: null';
  const newContent = `---\n${newFrontmatter}\n---${body}`;

  return { updated: true, content: newContent };
}

function main() {
  console.log('📂 Scanning for meeting files...');
  const meetingFiles = findMeetingFiles(MEETINGS_DIR);
  console.log(`   Found ${meetingFiles.length} meeting.md files`);
  console.log('');

  let updated = 0;
  let skipped = 0;
  let errors = 0;

  const toUpdate = [];
  const skippedFiles = [];

  for (const filePath of meetingFiles) {
    const relativePath = path.relative(VAULT_ROOT, filePath);

    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const result = addProcessedFields(content);

      if (result.updated) {
        toUpdate.push({ path: filePath, relativePath, content: result.content });
      } else {
        skipped++;
        skippedFiles.push({ relativePath, reason: result.reason });
      }
    } catch (error) {
      errors++;
      console.error(`   ❌ Error reading ${relativePath}: ${error.message}`);
    }
  }

  // Report what will be updated
  if (toUpdate.length > 0) {
    console.log(`📝 Files to update (${toUpdate.length}):`);
    for (const file of toUpdate) {
      console.log(`   - ${file.relativePath}`);
    }
    console.log('');
  }

  // Report skipped
  if (skippedFiles.length > 0) {
    console.log(`⏭️  Skipped (${skippedFiles.length}):`);
    for (const file of skippedFiles) {
      console.log(`   - ${file.relativePath} (${file.reason})`);
    }
    console.log('');
  }

  // Apply changes if not dry run
  if (!dryRun && toUpdate.length > 0) {
    console.log('💾 Applying changes...');
    for (const file of toUpdate) {
      try {
        fs.writeFileSync(file.path, file.content, 'utf8');
        updated++;
        console.log(`   ✅ ${file.relativePath}`);
      } catch (error) {
        errors++;
        console.error(`   ❌ Failed to write ${file.relativePath}: ${error.message}`);
      }
    }
    console.log('');
  } else if (toUpdate.length > 0) {
    updated = toUpdate.length;
  }

  // Summary
  console.log('📊 Summary:');
  console.log(`   ${dryRun ? 'Would update' : 'Updated'}: ${updated}`);
  console.log(`   Skipped: ${skipped}`);
  console.log(`   Errors: ${errors}`);

  if (dryRun && toUpdate.length > 0) {
    console.log('');
    console.log('💡 Run with --apply to make these changes');
  }
}

main();
