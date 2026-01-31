#!/usr/bin/env node
/**
 * SuperNormal Meeting Sync Script
 *
 * Automates downloading meeting transcripts and AI summaries from SuperNormal
 * to the Obsidian vault. Designed to be deterministic with minimal LLM involvement.
 *
 * Usage:
 *   node sync-meetings.js              # Interactive mode - syncs new meetings
 *   node sync-meetings.js --all        # Re-sync all meetings (overwrite existing)
 *   node sync-meetings.js --dry-run    # Show what would be downloaded without downloading
 *
 * Requirements:
 *   - Playwright installed: npm install playwright
 *   - Chrome browser available
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  // Vault paths
  vaultRoot: path.resolve(__dirname, '../../..'),
  meetingsDir: '5-Meetings',
  stateFile: path.join(__dirname, 'sync-state.json'),

  // SuperNormal URLs
  baseUrl: 'https://app.supernormal.com',
  meetingsUrl: 'https://app.supernormal.com/meetings',
  loginUrl: 'https://app.supernormal.com',

  // Browser settings
  headless: false,  // Show browser for login if needed
  slowMo: 100,      // Slow down for reliability
  timeout: 60000,   // 60 second timeout for operations

  // Sync settings
  maxMeetingsPerRun: 50,  // Limit meetings per sync run
};

// State management
function loadState() {
  try {
    if (fs.existsSync(CONFIG.stateFile)) {
      return JSON.parse(fs.readFileSync(CONFIG.stateFile, 'utf8'));
    }
  } catch (error) {
    console.warn('Could not load state file, starting fresh:', error.message);
  }
  return { downloadedMeetings: {}, lastSync: null };
}

function saveState(state) {
  state.lastSync = new Date().toISOString();
  fs.writeFileSync(CONFIG.stateFile, JSON.stringify(state, null, 2));
}

// Utility functions
function extractMeetingIdFromUrl(url) {
  // Extract the unique ID from URLs like:
  // /posts/meeting-on-december-05-2025-17-01-c32dc58f4c314b1da7f16d58920cb579
  const match = url.match(/\/posts\/([a-z0-9-]+)$/);
  return match ? match[1] : null;
}

function parseMeetingDate(dateText) {
  // Parse dates like "DEC 5, 2025", "JAN 7", "January 07, 2026", "December 22, 2025"
  const monthsShort = {
    'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04',
    'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
    'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'
  };
  const monthsFull = {
    'JANUARY': '01', 'FEBRUARY': '02', 'MARCH': '03', 'APRIL': '04',
    'MAY': '05', 'JUNE': '06', 'JULY': '07', 'AUGUST': '08',
    'SEPTEMBER': '09', 'OCTOBER': '10', 'NOVEMBER': '11', 'DECEMBER': '12'
  };

  // Try full month name first: "January 07, 2026" or "December 22, 2025"
  const fullMatch = dateText.match(/([A-Za-z]+)\s+(\d{1,2}),?\s*(\d{4})/);
  if (fullMatch) {
    const monthName = fullMatch[1].toUpperCase();
    const month = monthsFull[monthName] || monthsShort[monthName.substring(0, 3)];
    if (month) {
      const day = fullMatch[2].padStart(2, '0');
      const year = fullMatch[3];
      return `${year}-${month}-${day}`;
    }
  }

  // Try short month name: "DEC 5, 2025" or "JAN 7"
  const shortMatch = dateText.match(/([A-Z]{3})\s+(\d{1,2})(?:,\s*(\d{4}))?/i);
  if (shortMatch) {
    const month = monthsShort[shortMatch[1].toUpperCase()];
    if (month) {
      const day = shortMatch[2].padStart(2, '0');
      const year = shortMatch[3] || new Date().getFullYear().toString();
      return `${year}-${month}-${day}`;
    }
  }

  return null;
}

function getMonthName(monthNum) {
  const months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December'];
  return months[parseInt(monthNum) - 1];
}

function sanitizeFilename(name) {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .substring(0, 50);
}

function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * Detect and wait for Cloudflare challenge to be completed manually
 */
async function handleCloudflareChallenge(page) {
  // Check for Cloudflare challenge indicators
  const title = await page.title();
  const isCloudflare = title.toLowerCase().includes('just a moment') ||
                       title.toLowerCase().includes('cloudflare') ||
                       title.toLowerCase().includes('attention required');

  // Also check for the challenge checkbox/iframe
  const hasChallenge = await page.locator('iframe[src*="challenges"], #challenge-running, .cf-turnstile, input[name="cf-turnstile-response"]').isVisible().catch(() => false);

  if (isCloudflare || hasChallenge) {
    console.log('');
    console.log('🛡️  Cloudflare bot protection detected!');
    console.log('   Please complete the "Verify you are human" checkbox in the browser.');
    console.log('   The script will continue automatically once verified...');
    console.log('');

    // Wait for the challenge to be completed (page URL should change or title should change)
    // Use polling approach to avoid timeout issues
    const startTime = Date.now();
    const maxWait = 300000;  // 5 minutes
    while (Date.now() - startTime < maxWait) {
      try {
        const currentTitle = await page.title();
        const stillChallenge = currentTitle.toLowerCase().includes('just a moment') ||
                               currentTitle.toLowerCase().includes('cloudflare') ||
                               currentTitle.toLowerCase().includes('attention required');
        if (!stillChallenge) {
          break;
        }
      } catch (e) {
        // Context destroyed usually means page navigated - challenge completed
        break;
      }
      await page.waitForTimeout(1000);  // Check every second
    }

    console.log('✅ Cloudflare challenge completed!');
    // Wait for the new page to fully load
    await page.waitForLoadState('domcontentloaded').catch(() => {});
    await page.waitForTimeout(3000);  // Give page time to fully load
  }
}

// Main sync logic
async function main() {
  const args = process.argv.slice(2);
  const syncAll = args.includes('--all');
  const dryRun = args.includes('--dry-run');

  console.log('🚀 SuperNormal Meeting Sync');
  console.log(`   Mode: ${syncAll ? 'Full sync (all meetings)' : 'Incremental sync (new only)'}`);
  console.log(`   Dry run: ${dryRun ? 'Yes' : 'No'}`);
  console.log('');

  const state = loadState();

  // Launch browser using persistent context with real Chrome
  console.log('🌐 Launching browser...');

  // Use a dedicated user data directory for SuperNormal automation
  const userDataDir = path.join(__dirname, 'chrome-profile');

  // Launch with persistent context - this preserves login state between runs
  const context = await chromium.launchPersistentContext(userDataDir, {
    headless: CONFIG.headless,
    slowMo: CONFIG.slowMo,
    channel: 'chrome',  // Use installed Chrome for better compatibility
    args: [
      '--disable-blink-features=AutomationControlled',  // Hide automation
    ],
  });

  const page = context.pages()[0] || await context.newPage();
  page.setDefaultTimeout(CONFIG.timeout);

  // No separate browser object with persistent context
  const browser = null;

  try {
    // Step 1: Check login status
    console.log('🔑 Checking login status...');
    await page.goto(CONFIG.meetingsUrl);
    await page.waitForLoadState('domcontentloaded');

    // Check for Cloudflare challenge
    await handleCloudflareChallenge(page);

    // Give extra time for JavaScript to execute
    await page.waitForTimeout(2000);

    // Check if we're on the login page - use multiple indicators
    const currentUrl = page.url();
    const hasSignInText = await page.locator('text="Sign in to Supernormal"').isVisible().catch(() => false);
    const hasGoogleButton = await page.locator('text="Continue with Google"').isVisible().catch(() => false);
    const isLoginUrl = currentUrl.includes('signin') || currentUrl.includes('login');
    const isLoginPage = hasSignInText || hasGoogleButton || isLoginUrl;

    console.log(`   URL: ${currentUrl}`);
    console.log(`   Login page detected: ${isLoginPage} (text: ${hasSignInText}, google: ${hasGoogleButton}, url: ${isLoginUrl})`);

    if (isLoginPage) {
      console.log('');
      console.log('⚠️  Not logged in to SuperNormal.');
      console.log('   Please click "Continue with Google" and complete login.');
      console.log('   The script will continue automatically after login.');
      console.log('');

      // Wait for login page elements to disappear (user completed login)
      const startTime = Date.now();
      const maxWait = 300000;  // 5 minutes
      while (Date.now() - startTime < maxWait) {
        await page.waitForTimeout(2000);  // Check every 2 seconds

        // Check if login elements are still visible
        const stillOnLogin = await page.locator('text="Sign in to Supernormal"').isVisible().catch(() => false) ||
                             await page.locator('text="Continue with Google"').isVisible().catch(() => false);

        if (!stillOnLogin) {
          break;
        }
      }

      // Give the app time to load after login
      await page.waitForTimeout(3000);

      // Persistent context automatically saves login state
      console.log('✅ Login successful! State saved in chrome-profile/.');
    } else {
      console.log('✅ Already logged in');
    }

    // Step 2: Navigate to meetings list
    console.log('📋 Loading meetings list...');
    await page.goto(CONFIG.meetingsUrl);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // Wait for meetings to load - try multiple selectors
    console.log('   Waiting for meetings content...');
    try {
      // First try the heading
      await page.waitForSelector('h1:has-text("Meetings")', { timeout: 10000 });
      // Then wait for actual meeting links - they're in the main content area
      await page.waitForSelector('a[href^="/posts/"]', { timeout: 30000 });
    } catch (e) {
      // Try alternative: wait for any link in the content area
      console.log('   Trying alternative selector...');
      await page.waitForSelector('[href*="/posts/"]', { timeout: 15000 });
    }

    // Step 3: Extract meeting links
    console.log('🔍 Scanning for meetings...');
    const meetings = await extractMeetings(page);
    console.log(`   Found ${meetings.length} meetings`);

    // Step 4: Filter meetings to sync
    const meetingsToSync = meetings.filter(m => {
      if (syncAll) return true;
      return !state.downloadedMeetings[m.id];
    });

    if (meetingsToSync.length === 0) {
      console.log('✅ No new meetings to sync!');
    } else {
      console.log(`📥 ${meetingsToSync.length} meetings to download`);

      if (dryRun) {
        console.log('');
        console.log('Would download:');
        meetingsToSync.slice(0, 10).forEach(m => {
          console.log(`   - ${m.title} (${m.date})`);
        });
        if (meetingsToSync.length > 10) {
          console.log(`   ... and ${meetingsToSync.length - 10} more`);
        }
      } else {
        // Step 5: Download each meeting
        let successCount = 0;
        let errorCount = 0;

        for (let i = 0; i < Math.min(meetingsToSync.length, CONFIG.maxMeetingsPerRun); i++) {
          const meeting = meetingsToSync[i];
          console.log(`\n[${i + 1}/${meetingsToSync.length}] ${meeting.title}`);

          try {
            const result = await downloadMeeting(page, context, meeting);
            state.downloadedMeetings[meeting.id] = {
              downloadedAt: new Date().toISOString(),
              outputPath: result.outputPath,
            };
            successCount++;
            console.log(`   ✅ Saved to ${result.outputPath}`);
          } catch (error) {
            errorCount++;
            console.error(`   ❌ Error: ${error.message}`);
          }
        }

        // Save state
        saveState(state);

        console.log('');
        console.log(`📊 Summary: ${successCount} downloaded, ${errorCount} errors`);
      }
    }

  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  } finally {
    // Close persistent context (this saves state automatically)
    await context.close();
  }
}

async function extractMeetings(page) {
  const meetings = [];

  // Get all meeting links
  const links = await page.locator('a[href^="/posts/"]').all();

  for (const link of links) {
    try {
      const href = await link.getAttribute('href');
      const id = extractMeetingIdFromUrl(href);
      if (!id) continue;

      // Get the meeting title from the heading inside
      const titleEl = link.locator('h3').first();
      const titleText = await titleEl.textContent().catch(() => '');

      // Parse title to extract meeting name and time
      // Format: "Meeting on December 05, 2025 17:01 11:01 AM ›"
      const titleMatch = titleText.match(/^(.+?)\s+(\d{1,2}:\d{2}\s*(?:AM|PM))\s*›?$/);
      const title = titleMatch ? titleMatch[1].trim() : titleText.replace(/›/g, '').trim();

      // Get the summary text
      const summaryEl = link.locator('div').last();
      const summary = await summaryEl.textContent().catch(() => '');

      // Try to find the date header above this link
      // We'll extract it from the title which contains the date
      const dateMatch = title.match(/(\w+)\s+(\d{1,2}),?\s*(\d{4})?/);
      let date = null;
      if (dateMatch) {
        date = parseMeetingDate(`${dateMatch[1]} ${dateMatch[2]}${dateMatch[3] ? ', ' + dateMatch[3] : ''}`);
      }

      meetings.push({
        id,
        url: `${CONFIG.baseUrl}${href}`,
        title,
        summary,
        date: date || new Date().toISOString().slice(0, 10),
      });
    } catch (error) {
      // Skip meetings that can't be parsed
      console.warn('   Skipping meeting due to parse error');
    }
  }

  return meetings;
}

async function downloadMeeting(page, context, meeting) {
  // Navigate to meeting page
  await page.goto(meeting.url);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2000);

  // Wait for meeting content to load - use multiple indicators
  // The page takes a few seconds to fully render after navigation
  await page.waitForTimeout(3000);  // Initial wait for React to render

  // Try multiple selectors for meeting content
  try {
    await page.waitForSelector('button:has-text("Notes"), [role="banner"], input[placeholder*="title" i], textbox[placeholder*="title" i]', { timeout: 30000 });
  } catch (e) {
    // If standard selectors fail, just wait a bit more and proceed
    console.log('   Waiting for page to fully load...');
    await page.waitForTimeout(5000);
  }

  // Extract notes using clipboard (more reliable than DOM scraping)
  console.log('   📝 Extracting notes via clipboard...');
  const notesText = await copyContentViaMenu(page, context, 'Copy notes');

  // Extract transcript using clipboard
  console.log('   📜 Extracting transcript via clipboard...');
  const transcriptText = await copyContentViaMenu(page, context, 'Copy transcript');

  // Extract attendees from both sources
  const attendeesFromNotes = extractAttendeesFromNotes(notesText);
  const attendeesFromTranscript = extractAttendeesFromTranscript(transcriptText);
  const allAttendees = [...new Set([...attendeesFromNotes, ...attendeesFromTranscript])];
  console.log(`   👥 Detected attendees: ${allAttendees.join(', ') || 'none'}`);

  // Detect company from content and attendees
  const company = detectCompany(allAttendees, notesText, transcriptText);
  console.log(`   🏢 Detected company: ${company || 'unknown'}`);

  // Extract meeting time from notes header (line 2 usually has "Wednesday, January 7th @ 11:15 AM")
  let meetingTime = '';
  if (notesText) {
    const timeMatch = notesText.match(/@\s*(\d{1,2}:\d{2}\s*(?:AM|PM))/i);
    if (timeMatch) {
      meetingTime = timeMatch[1];
    }
  }

  // Extract clean meeting title
  const meetingTitle = extractMeetingTitle(notesText, meeting.title);
  console.log(`   📋 Meeting title: ${meetingTitle}`);

  // Get meeting metadata (enhanced)
  const metadata = await extractMetadata(page, meeting);
  metadata.attendees = allAttendees;
  metadata.company = company;
  metadata.cleanTitle = meetingTitle;
  metadata.time = meetingTime;

  // Determine output directory using new format
  const [year, month, day] = meeting.date.split('-');
  const monthName = getMonthName(month);
  const folderName = formatFolderName(meeting.date, meetingTime, company, meetingTitle);

  const outputDir = path.join(
    CONFIG.vaultRoot,
    CONFIG.meetingsDir,
    year,
    `${month}-${monthName}`,
    folderName
  );

  ensureDirectoryExists(outputDir);

  // Write notes file with frontmatter header
  const notesWithHeader = formatNotesWithHeader(notesText, {
    title: meetingTitle,
    date: meeting.date,
    company: company,
    attendees: allAttendees,
  });
  fs.writeFileSync(path.join(outputDir, 'notes-supernormal.md'), notesWithHeader);

  // Write transcript file with frontmatter header
  const transcriptWithHeader = formatTranscriptWithHeader(transcriptText, {
    title: meetingTitle,
    date: meeting.date,
    company: company,
    attendees: allAttendees,
  });
  fs.writeFileSync(path.join(outputDir, 'transcript.md'), transcriptWithHeader);

  // Create main meeting file if it doesn't exist
  const meetingFilePath = path.join(outputDir, 'meeting.md');
  if (!fs.existsSync(meetingFilePath)) {
    const meetingContent = formatMeetingMarkdown(notesText, metadata);
    fs.writeFileSync(meetingFilePath, meetingContent);
  }

  return { outputPath: outputDir };
}

/**
 * Click the menu button and copy content via "Copy notes" or "Copy transcript" button
 * Uses clipboard API for reliable content extraction
 */
async function copyContentViaMenu(page, context, menuItemText) {
  try {
    // Grant clipboard permissions
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);

    // Strategy: Find all clickable buttons in the page header, try each until we find
    // one that opens a menu containing "Copy notes"
    const menuOpened = await openMeetingMenu(page);
    if (!menuOpened) {
      throw new Error('Could not open meeting menu');
    }

    // Click the desired menu item
    const menuItem = page.locator(`[role="menuitem"]:has-text("${menuItemText}"), button:has-text("${menuItemText}")`).first();
    const menuItemVisible = await menuItem.isVisible().catch(() => false);

    if (!menuItemVisible) {
      // Menu might have closed, try opening again
      await openMeetingMenu(page);
    }

    await menuItem.click();
    await page.waitForTimeout(500);  // Wait for copy to complete

    // Look for "Copied!" confirmation text that appears briefly
    const copiedConfirmation = await page.locator('text=Copied').isVisible().catch(() => false);
    if (copiedConfirmation) {
      console.log(`   ✓ ${menuItemText} copied`);
    }

    // Read from clipboard
    const clipboardContent = await page.evaluate(async () => {
      try {
        return await navigator.clipboard.readText();
      } catch (e) {
        return null;
      }
    });

    if (clipboardContent) {
      return clipboardContent;
    }

    // Fallback: try reading via CDP if direct clipboard access fails
    console.log(`   ⚠️  Direct clipboard access failed, trying alternative method...`);
    return await readClipboardViaCDP(context);

  } catch (error) {
    console.warn(`   ⚠️  Could not copy via menu: ${error.message}`);
    return null;
  }
}

/**
 * Find and open the meeting options menu (contains Copy notes, Copy transcript, etc.)
 * Returns true if menu was successfully opened
 */
async function openMeetingMenu(page) {
  // First, check if menu is already open
  const menuAlreadyOpen = await page.locator('[role="menu"]:has-text("Copy notes")').isVisible().catch(() => false);
  if (menuAlreadyOpen) {
    return true;
  }

  // CRITICAL: Dismiss any existing overlays by clicking on the #menu-root overlay
  // SuperNormal uses Radix UI which creates a presentation overlay when any popup is open
  // This overlay intercepts ALL pointer events until dismissed
  const overlayDismissed = await page.evaluate(() => {
    const overlay = document.querySelector('#menu-root div[role="presentation"]');
    if (overlay) {
      overlay.click();
      return true;
    }
    return false;
  });
  if (overlayDismissed) {
    await page.waitForTimeout(300);
  }

  // Also press Escape to close any menus
  await page.keyboard.press('Escape');
  await page.waitForTimeout(200);

  // Strategy 1: Find the banner and click the SECOND button (menu button)
  // In SuperNormal's UI:
  //   - First button in header = Integrations popup
  //   - Second button in header = Meeting menu (Copy notes, Copy transcript, etc.)
  const banner = page.locator('[role="banner"]');
  const bannerExists = await banner.isVisible().catch(() => false);

  if (bannerExists) {
    // Get all buttons in the banner
    const buttons = await banner.locator('button').all();
    console.log(`   Found ${buttons.length} buttons in banner`);

    // The menu button is typically the SECOND button (index 1)
    // But we should also check by position - it's after the Integrations button
    for (let i = 1; i < buttons.length; i++) {  // Start at 1, skip first button
      const btn = buttons[i];
      const isVisible = await btn.isVisible().catch(() => false);
      if (!isVisible) continue;

      const text = await btn.textContent().catch(() => '');
      // Skip buttons with text (the menu button has no visible text)
      if (text.trim().length > 2) continue;

      console.log(`   Trying banner button ${i}...`);

      // Dismiss overlay again before clicking (in case one appeared)
      await page.evaluate(() => {
        const overlay = document.querySelector('#menu-root div[role="presentation"]');
        if (overlay) overlay.click();
      });
      await page.waitForTimeout(100);

      try {
        await btn.click();
        await page.waitForTimeout(500);

        // Check if the correct menu appeared
        const menuAppeared = await page.locator('[role="menu"]:has-text("Copy notes"), [role="menuitem"]:has-text("Copy notes")').isVisible().catch(() => false);
        if (menuAppeared) {
          console.log(`   ✓ Menu opened via banner button ${i}`);
          return true;
        }

        // Close any wrong menu that opened
        await page.evaluate(() => {
          const overlay = document.querySelector('#menu-root div[role="presentation"]');
          if (overlay) overlay.click();
        });
        await page.keyboard.press('Escape');
        await page.waitForTimeout(200);
      } catch (e) {
        console.log(`   Click failed: ${e.message.slice(0, 50)}`);
      }
    }
  }

  // Strategy 2: Find buttons near the "Meetings" breadcrumb link
  const meetingsLink = page.locator('a:has-text("Meetings")').first();
  const hasLink = await meetingsLink.isVisible().catch(() => false);

  if (hasLink) {
    // Navigate up to find the container with action buttons
    const container = meetingsLink.locator('xpath=ancestor::*[3]');
    const buttons = await container.locator('button').all();

    console.log(`   Found ${buttons.length} buttons near breadcrumb`);

    // Try buttons from the end (menu button is usually last or second-to-last)
    for (let i = buttons.length - 1; i >= 0; i--) {
      const btn = buttons[i];
      const isVisible = await btn.isVisible().catch(() => false);
      if (!isVisible) continue;

      const text = await btn.textContent().catch(() => '');
      if (text.trim().length > 5) continue;

      // Dismiss overlay before clicking
      await page.evaluate(() => {
        const overlay = document.querySelector('#menu-root div[role="presentation"]');
        if (overlay) overlay.click();
      });
      await page.waitForTimeout(100);

      try {
        await btn.click();
        await page.waitForTimeout(500);

        const menuAppeared = await page.locator('[role="menu"]:has-text("Copy notes")').isVisible().catch(() => false);
        if (menuAppeared) {
          console.log(`   ✓ Menu opened via breadcrumb area button`);
          return true;
        }

        await page.evaluate(() => {
          const overlay = document.querySelector('#menu-root div[role="presentation"]');
          if (overlay) overlay.click();
        });
        await page.keyboard.press('Escape');
        await page.waitForTimeout(200);
      } catch (e) {
        // Try next button
      }
    }
  }

  // Strategy 3: Direct selector for buttons with aria-haspopup="menu"
  const menuButtons = await page.locator('button[aria-haspopup="menu"]').all();
  console.log(`   Found ${menuButtons.length} menu trigger buttons`);

  for (const btn of menuButtons) {
    const isVisible = await btn.isVisible().catch(() => false);
    if (!isVisible) continue;

    // Dismiss overlay before clicking
    await page.evaluate(() => {
      const overlay = document.querySelector('#menu-root div[role="presentation"]');
      if (overlay) overlay.click();
    });
    await page.waitForTimeout(100);

    try {
      await btn.click();
      await page.waitForTimeout(500);

      const menuAppeared = await page.locator('[role="menu"]:has-text("Copy notes")').isVisible().catch(() => false);
      if (menuAppeared) {
        console.log(`   ✓ Menu opened via aria-haspopup button`);
        return true;
      }

      await page.evaluate(() => {
        const overlay = document.querySelector('#menu-root div[role="presentation"]');
        if (overlay) overlay.click();
      });
      await page.keyboard.press('Escape');
      await page.waitForTimeout(200);
    } catch (e) {
      // Try next button
    }
  }

  console.log(`   ⚠️ Could not find menu button`);
  return false;
}

/**
 * Fallback clipboard reading via Chrome DevTools Protocol
 */
async function readClipboardViaCDP(context) {
  try {
    const cdpSession = await context.newCDPSession(await context.pages()[0]);
    const { data } = await cdpSession.send('Browser.getClipboard', { mediaType: 'text/plain' });
    return data;
  } catch (e) {
    return null;
  }
}

// NOTE: extractNotes() and extractTranscript() removed - now using clipboard-based extraction
// via copyContentViaMenu() which is more reliable than DOM scraping

async function extractMetadata(page, meeting) {
  const metadata = {
    title: meeting.title,
    date: meeting.date,
    url: meeting.url,
    duration: '',
    participants: [],
  };

  try {
    // Extract duration
    const durationEl = page.locator('p:has-text("min")').first();
    metadata.duration = await durationEl.textContent().catch(() => '');

    // Extract participant count
    const participantEl = page.locator('p:has-text("participant")').first();
    metadata.participantCount = await participantEl.textContent().catch(() => '');
  } catch (error) {
    // Metadata extraction is optional
  }

  return metadata;
}

// NOTE: formatNotesMarkdown() and formatTranscriptMarkdown() removed
// Now using raw clipboard content directly from SuperNormal's "Copy notes"/"Copy transcript" buttons

/**
 * Load known people from contacts-config.json for reliable attendee detection.
 * Falls back to minimal defaults if config is missing or invalid.
 *
 * @returns {Object} Map of lowercase name/alias -> display name
 */
function loadKnownPeople() {
  const contactsConfigPath = path.join(CONFIG.vaultRoot, '0-System/config/contacts-config.json');
  const knownPeople = {
    // Self always included (uses placeholder, resolved at runtime)
    'user': '{{user_name}}',
  };

  try {
    if (!fs.existsSync(contactsConfigPath)) {
      console.warn('contacts-config.json not found, using minimal defaults');
      return knownPeople;
    }

    const config = JSON.parse(fs.readFileSync(contactsConfigPath, 'utf8'));

    // Add company contacts
    if (config.companies) {
      for (const company of Object.values(config.companies)) {
        if (company.contacts && Array.isArray(company.contacts)) {
          for (const contact of company.contacts) {
            if (contact.name) {
              // Add full name
              knownPeople[contact.name.toLowerCase()] = contact.name;

              // Add aliases
              if (contact.aliases && Array.isArray(contact.aliases)) {
                for (const alias of contact.aliases) {
                  knownPeople[alias.toLowerCase()] = contact.name;
                }
              }
            }
          }
        }
      }
    }

    // Add collaborators
    if (config.collaborators && Array.isArray(config.collaborators)) {
      for (const contact of config.collaborators) {
        if (contact.name) {
          knownPeople[contact.name.toLowerCase()] = contact.name;
          if (contact.aliases && Array.isArray(contact.aliases)) {
            for (const alias of contact.aliases) {
              knownPeople[alias.toLowerCase()] = contact.name;
            }
          }
        }
      }
    }

    // Add personal contacts
    if (config.personal) {
      if (config.personal.partner) {
        const partner = config.personal.partner;
        if (typeof partner === 'string') {
          knownPeople['partner'] = partner;
          knownPeople[partner.toLowerCase()] = partner;
        } else if (partner.name) {
          knownPeople['partner'] = partner.name;
          knownPeople[partner.name.toLowerCase()] = partner.name;
        }
      }

      if (config.personal.children && Array.isArray(config.personal.children)) {
        for (const child of config.personal.children) {
          if (typeof child === 'string') {
            knownPeople[child.toLowerCase()] = child;
          } else if (child.name) {
            knownPeople[child.name.toLowerCase()] = child.name;
          }
        }
      }
    }

    console.log(`Loaded ${Object.keys(knownPeople).length} known people entries from config`);
    return knownPeople;

  } catch (error) {
    console.warn('Error loading contacts-config.json:', error.message);
    return knownPeople;
  }
}

// Known team members and associates - loaded dynamically from contacts-config.json
const KNOWN_PEOPLE = loadKnownPeople();

/**
 * Load company keywords from contacts-config.json for meeting categorization.
 * Falls back to empty arrays if config is missing or invalid.
 *
 * @returns {Object} Map of company key -> keywords array
 */
function loadCompanyKeywords() {
  const contactsConfigPath = path.join(CONFIG.vaultRoot, '0-System/config/contacts-config.json');
  const keywords = {
    company_1: [],
    company_2: [],
    company_3: []
  };

  try {
    if (!fs.existsSync(contactsConfigPath)) {
      console.warn('contacts-config.json not found, company keywords will be empty');
      return keywords;
    }

    const config = JSON.parse(fs.readFileSync(contactsConfigPath, 'utf8'));

    if (config.companies) {
      if (config.companies.company_1?.keywords && Array.isArray(config.companies.company_1.keywords)) {
        keywords.company_1 = config.companies.company_1.keywords;
      }
      if (config.companies.company_2?.keywords && Array.isArray(config.companies.company_2.keywords)) {
        keywords.company_2 = config.companies.company_2.keywords;
      }
      if (config.companies.company_3?.keywords && Array.isArray(config.companies.company_3.keywords)) {
        keywords.company_3 = config.companies.company_3.keywords;
      }
    }

    const totalKeywords = keywords.company_1.length + keywords.company_2.length + keywords.company_3.length;
    if (totalKeywords > 0) {
      console.log(`Loaded ${totalKeywords} company keywords from config`);
    }

    return keywords;

  } catch (error) {
    console.warn('Error loading company keywords:', error.message);
    return keywords;
  }
}

/**
 * Extract ACTUAL attendees from transcript using greeting/joining patterns
 *
 * SuperNormal doesn't track attendees explicitly and has no speaker diarization.
 * Simply searching for known names catches people who were DISCUSSED but not present.
 *
 * This function looks for conversational patterns that indicate someone actually
 * joined the meeting (greetings, acknowledgments of joining).
 *
 * Returns only {{user_first_name}} (meeting owner) by default, plus anyone who shows clear
 * patterns of being greeted/joining.
 */
function extractAttendeesFromTranscript(transcriptText) {
  if (!transcriptText) return ['{{user_name}}'];

  const attendees = new Set(['{{user_name}}']); // Owner always present

  // Patterns that indicate someone JOINED the meeting (not just mentioned)
  // These patterns look for greetings directed AT someone or acknowledgments
  const joiningPatterns = [
    // "Hey Alex" / "Hi Sam" / "Hello Taylor" - greeting someone who just joined
    /\b(?:hey|hi|hello|what'?s up|good morning|good afternoon)\s+([A-Z][a-z]+)(?:\s|[.!?,]|$)/gi,

    // "Alex, how are you" - addressing someone by name
    /\b([A-Z][a-z]+),?\s+(?:how are you|good to see you|glad you.?re here)/gi,

    // "Welcome [name]" patterns
    /\bwelcome\s+([A-Z][a-z]+)/gi,
  ];

  for (const pattern of joiningPatterns) {
    let match;
    while ((match = pattern.exec(transcriptText)) !== null) {
      const name = match[1].toLowerCase();
      // Only add if it's a known person (not random words that happen to be capitalized)
      if (KNOWN_PEOPLE[name]) {
        attendees.add(KNOWN_PEOPLE[name]);
      }
    }
  }

  return Array.from(attendees);
}

/**
 * Extract attendees from notes text based ONLY on task assignments
 *
 * Task assignments ("- {{user_name}}: Task") indicate the person was present
 * and was assigned a task. This is more reliable than general name mentions
 * which could be people being discussed.
 *
 * Note: This still isn't perfect since tasks can be assigned to people not
 * in the meeting, but it's more accurate than keyword matching.
 */
function extractAttendeesFromNotes(notesText) {
  if (!notesText) return [];

  const attendees = new Set();

  // Look for task assignments like "- {{user_name}}: ..." (SuperNormal format)
  // This indicates someone who was likely present and given an action item
  const taskPattern = /^-\s+([A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+)?)\s*:/gm;
  let match;
  while ((match = taskPattern.exec(notesText)) !== null) {
    const name = match[1].trim();
    if (name && name !== 'Unassigned') {
      // Normalize to known person if possible
      const nameLower = name.toLowerCase();
      if (KNOWN_PEOPLE[nameLower]) {
        attendees.add(KNOWN_PEOPLE[nameLower]);
      } else {
        attendees.add(name);
      }
    }
  }

  // Note: We deliberately do NOT scan for general name mentions anymore
  // because that catches people who were discussed but not present

  return Array.from(attendees);
}

/**
 * Detect company from attendees and content keywords
 */
function detectCompany(attendees, notesText, transcriptText) {
  const allText = `${notesText || ''} ${transcriptText || ''}`.toLowerCase();
  const attendeeNames = attendees.map(a => a.toLowerCase());

  // Load company contacts from config for detection
  const contactsConfigPath = path.join(CONFIG.vaultRoot, '0-System/config/contacts-config.json');
  let artBlocksAttendees = [];
  let oneFortyFourAttendees = [];
  let emhAttendees = ['partner'];

  try {
    if (fs.existsSync(contactsConfigPath)) {
      const config = JSON.parse(fs.readFileSync(contactsConfigPath, 'utf8'));
      if (config.companies?.company_1?.contacts) {
        artBlocksAttendees = config.companies.company_1.contacts.flatMap(c =>
          [c.name?.toLowerCase(), ...(c.aliases || [])].filter(Boolean)
        );
      }
      if (config.companies?.company_2?.contacts) {
        oneFortyFourAttendees = config.companies.company_2.contacts.flatMap(c =>
          [c.name?.toLowerCase(), ...(c.aliases || [])].filter(Boolean)
        );
      }
      if (config.personal?.partner) {
        const partner = config.personal.partner;
        emhAttendees = [typeof partner === 'string' ? partner.toLowerCase() : partner.name?.toLowerCase()].filter(Boolean);
      }
    }
  } catch (error) {
    console.warn('Could not load contacts for company detection:', error.message);
  }

  // Load company keywords dynamically from contacts-config.json
  const companyKeywords = loadCompanyKeywords();
  const artBlocksKeywords = companyKeywords.company_1 || [];
  const oneFortyFourKeywords = companyKeywords.company_2 || [];
  const emhKeywords = companyKeywords.company_3 || [];

  // Score each company
  let scores = { ab: 0, '144': 0, emh: 0, personal: 0 };

  // Check attendees
  for (const attendee of attendeeNames) {
    if (artBlocksAttendees.some(a => attendee.includes(a))) scores.ab += 3;
    if (oneFortyFourAttendees.some(a => attendee.includes(a))) scores['144'] += 3;
    if (emhAttendees.some(a => attendee.includes(a))) scores.emh += 3;
  }

  // Check keywords in content
  for (const kw of artBlocksKeywords) {
    if (allText.includes(kw)) scores.ab += 2;
  }
  for (const kw of oneFortyFourKeywords) {
    if (allText.includes(kw)) scores['144'] += 2;
  }
  for (const kw of emhKeywords) {
    if (allText.includes(kw)) scores.emh += 2;
  }

  // Determine winner
  const maxScore = Math.max(scores.ab, scores['144'], scores.emh, scores.personal);
  if (maxScore === 0) return null;

  if (scores.ab === maxScore) return 'ab';
  if (scores['144'] === maxScore) return '144';
  if (scores.emh === maxScore) return 'emh';
  return 'personal';
}

/**
 * Extract a clean meeting title from the SuperNormal title
 * Input: "Meeting on January 07, 2026 16:0210:02 AM" or similar
 * Output: Clean title like "Product Sync" or original if can't parse better
 */
function extractMeetingTitle(notesText, rawTitle) {
  // If we can find a better title from the notes content, use it
  // Otherwise clean up the raw title

  // Clean up the raw title - remove redundant time formats
  let cleanTitle = rawTitle
    .replace(/\s+\d{1,2}:\d{2}\s*(?:AM|PM)\s*›?/g, '')  // Remove time like "10:02 AM"
    .replace(/\d{2}:\d{2}(?:\d{2}:\d{2})?/g, '')  // Remove time patterns like "16:02" or "16:0210:02"
    .trim();

  // If title is generic like "Meeting on DATE", try to extract something better
  if (cleanTitle.match(/^Meeting on/i)) {
    // Look for meeting type keywords in the notes
    const keywords = [
      { pattern: /product\s*(?:sync|meeting|call)/i, title: 'Product Sync' },
      { pattern: /standup/i, title: 'Standup' },
      { pattern: /planning/i, title: 'Planning' },
      { pattern: /retrospective|retro/i, title: 'Retrospective' },
      { pattern: /1[:\s]*(?:on)?[:\s]*1|one[:\s]*(?:on)?[:\s]*one/i, title: '1:1' },
      { pattern: /kickoff|kick[:\s-]*off/i, title: 'Kickoff' },
      { pattern: /review/i, title: 'Review' },
      { pattern: /sync/i, title: 'Sync' },
    ];

    if (notesText) {
      for (const { pattern, title } of keywords) {
        if (pattern.test(notesText)) {
          return title;
        }
      }
    }

    // Default to just the date part
    const dateMatch = cleanTitle.match(/on\s+([A-Za-z]+\s+\d{1,2})/);
    return dateMatch ? `Meeting ${dateMatch[1]}` : cleanTitle;
  }

  return cleanTitle || rawTitle;
}

/**
 * Format the folder name with company and meeting title
 * Format: YYYY-MM-DD-HH-MM-{company}-{meetingname}
 */
function formatFolderName(date, time, company, meetingTitle) {
  const [year, month, day] = date.split('-');

  // Parse time - could be "10:02 AM", "16:02", etc.
  let hour = '00';
  let minute = '00';

  // Try to extract time from various formats
  const time24Match = time?.match(/(\d{1,2}):(\d{2})/);
  const time12Match = time?.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);

  if (time12Match) {
    let h = parseInt(time12Match[1]);
    const m = time12Match[2];
    const ampm = time12Match[3].toUpperCase();
    if (ampm === 'PM' && h < 12) h += 12;
    if (ampm === 'AM' && h === 12) h = 0;
    hour = h.toString().padStart(2, '0');
    minute = m;
  } else if (time24Match) {
    hour = time24Match[1].padStart(2, '0');
    minute = time24Match[2];
  }

  // Build folder name
  let folderName = `${year}-${month}-${day}-${hour}-${minute}`;

  if (company) {
    folderName += `-${company}`;
  }

  if (meetingTitle) {
    folderName += `-${sanitizeFilename(meetingTitle)}`;
  }

  return folderName;
}

/**
 * Format notes file with header metadata
 */
function formatNotesWithHeader(notesText, metadata) {
  const header = `---
title: "${metadata.title}"
date: "${metadata.date}"
company: "${metadata.company || ''}"
attendees: [${metadata.attendees.map(a => `"${a}"`).join(', ')}]
source: "supernormal"
---

`;
  return header + (notesText || '(No notes available)');
}

/**
 * Format transcript file with header metadata
 */
function formatTranscriptWithHeader(transcriptText, metadata) {
  const header = `---
title: "${metadata.title}"
date: "${metadata.date}"
company: "${metadata.company || ''}"
attendees: [${metadata.attendees.map(a => `"${a}"`).join(', ')}]
source: "supernormal"
---

`;
  return header + (transcriptText || '(No transcript available)');
}

function formatMeetingMarkdown(notesText, metadata) {
  const [year, month, day] = metadata.date.split('-');

  // Extract tasks from the notes text if possible
  const taskLines = [];
  const userTasks = [];
  const othersTasks = [];
  const unassignedTasks = [];

  if (notesText) {
    const lines = notesText.split('\n');
    for (const line of lines) {
      // Look for SuperNormal task format: "- Name: Task description"
      const taskMatch = line.match(/^-\s+([^:]+):\s+(.+)$/);
      if (taskMatch) {
        const assignee = taskMatch[1].trim();
        const task = taskMatch[2].trim();
        if (assignee.toLowerCase().includes('user')) {
          userTasks.push(task);
        } else if (assignee === 'Unassigned') {
          unassignedTasks.push(task);
        } else {
          othersTasks.push(`${task} (@${assignee})`);
        }
      } else if (line.match(/^[-*]\s*\[[ x]\]/) || line.match(/^(Action|TODO|Task):/i)) {
        // Fallback for other task formats
        taskLines.push(line.replace(/^[-*]\s*\[[ x]\]\s*/, '').trim());
      }
    }
  }

  // Build attendees list for display
  const attendeesList = metadata.attendees && metadata.attendees.length > 0
    ? metadata.attendees.map(a => `[[${a}]]`).join(', ')
    : '<!-- Add attendees -->';

  // Company display name
  const companyNames = { ab: '{{company_1_name}}', '144': '{{company_2_name}}', emh: '{{company_3_name}}', personal: 'Personal' };
  const companyDisplay = companyNames[metadata.company] || '';

  // Use clean title if available
  const displayTitle = metadata.cleanTitle || metadata.title;

  return `---
title: "${displayTitle}"
date: "${metadata.date}"
company: "${metadata.company || ''}"
attendees: [${(metadata.attendees || []).map(a => `"${a}"`).join(', ')}]
source: "supernormal"
has_artifacts: true
processed: false
processed_date: null
---

# ${displayTitle}

**Company**: ${companyDisplay || '<!-- Add company -->'}
**Attendees**: ${attendeesList}
**Time**: ${metadata.time || '<!-- Add time -->'}

## Key Topics

<!-- Review the AI notes and transcript, then summarize key topics discussed -->

## Decisions

<!-- Any decisions made during the meeting -->

## Artifacts

- [[notes-supernormal|Supernormal AI Notes]]
- [[transcript|Full Transcript]]

## Action Items

### Assigned to {{user_first_name}}
${userTasks.length > 0 ? userTasks.map(t => `- [ ] ${t}`).join('\n') : '- [ ] Review meeting notes'}

### Assigned to Others
${othersTasks.length > 0 ? othersTasks.map(t => `- [ ] ${t}`).join('\n') : '<!-- Move tasks here that are assigned to others -->'}

### Unassigned
${unassignedTasks.length > 0 ? unassignedTasks.map(t => `- [ ] ${t}`).join('\n') : '<!-- Add unassigned tasks here -->'}

## Related

<!-- Add links to related notes, projects, or people -->
${(metadata.attendees || []).map(a => `- [[${a}]]`).join('\n') || ''}
`;
}

// Run main function
main().catch(console.error);
