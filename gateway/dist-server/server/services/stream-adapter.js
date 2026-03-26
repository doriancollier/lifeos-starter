export function initSSEStream(res) {
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        Connection: 'keep-alive',
        'X-Accel-Buffering': 'no',
    });
}
export function sendSSEEvent(res, event) {
    res.write(`event: ${event.type}\n`);
    res.write(`data: ${JSON.stringify(event.data)}\n\n`);
}
export function endSSEStream(res) {
    res.end();
}
//# sourceMappingURL=stream-adapter.js.map