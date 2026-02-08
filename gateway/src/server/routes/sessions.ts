import path from 'path';
import { fileURLToPath } from 'url';
import { Router } from 'express';
import { agentManager } from '../services/agent-manager';
import { transcriptReader } from '../services/transcript-reader';
import { initSSEStream, sendSSEEvent, endSSEStream } from '../services/stream-adapter';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const vaultRoot = path.resolve(__dirname, '../../../../');

const router = Router();

// POST /api/sessions - Create new session
// Sends an initial message to the SDK to generate the session JSONL file,
// then returns the session metadata.
router.post('/', async (req, res) => {
  const { permissionMode = 'default' } = req.body;

  // Use SDK's query() with a no-op prompt to establish the session.
  // The SDK will create the JSONL file and assign a session ID.
  // We need to send a real first message, so we'll just create an in-memory
  // session entry and let the first POST /messages call create the JSONL.
  const sessionId = crypto.randomUUID();
  agentManager.ensureSession(sessionId, { permissionMode });

  res.json({
    id: sessionId,
    title: `New Session`,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    permissionMode,
  });
});

// GET /api/sessions - List all sessions from SDK transcripts
router.get('/', async (req, res) => {
  const limit = Math.min(Number(req.query.limit) || 200, 500);
  const sessions = await transcriptReader.listSessions(vaultRoot);
  res.json(sessions.slice(0, limit));
});

// GET /api/sessions/:id - Get session details
router.get('/:id', async (req, res) => {
  const session = await transcriptReader.getSession(vaultRoot, req.params.id);
  if (!session) return res.status(404).json({ error: 'Session not found' });
  res.json(session);
});

// GET /api/sessions/:id/messages - Get message history from SDK transcript
router.get('/:id/messages', async (req, res) => {
  const messages = await transcriptReader.readTranscript(vaultRoot, req.params.id);
  res.json({ messages });
});

// POST /api/sessions/:id/messages - Send message (SSE stream response)
router.post('/:id/messages', async (req, res) => {
  const { content } = req.body;
  if (!content) return res.status(400).json({ error: 'content is required' });

  const sessionId = req.params.id;

  initSSEStream(res);

  try {
    for await (const event of agentManager.sendMessage(sessionId, content)) {
      sendSSEEvent(res, event);

      // If SDK assigned a different session ID, track it
      if (event.type === 'done') {
        const actualSdkId = agentManager.getSdkSessionId(sessionId);
        if (actualSdkId && actualSdkId !== sessionId) {
          // Send a redirect hint so the client can update its session ID
          sendSSEEvent(res, {
            type: 'done',
            data: { sessionId: actualSdkId },
          });
        }
      }
    }
  } catch (err) {
    sendSSEEvent(res, {
      type: 'error',
      data: { message: err instanceof Error ? err.message : 'Unknown error' },
    });
  } finally {
    endSSEStream(res);
  }
});

// POST /api/sessions/:id/approve - Approve pending tool call
router.post('/:id/approve', async (req, res) => {
  const { toolCallId } = req.body;
  const approved = agentManager.approveTool(req.params.id, toolCallId, true);
  if (!approved) return res.status(404).json({ error: 'No pending approval' });
  res.json({ ok: true });
});

// POST /api/sessions/:id/deny - Deny pending tool call
router.post('/:id/deny', async (req, res) => {
  const { toolCallId } = req.body;
  const denied = agentManager.approveTool(req.params.id, toolCallId, false);
  if (!denied) return res.status(404).json({ error: 'No pending approval' });
  res.json({ ok: true });
});

export default router;
